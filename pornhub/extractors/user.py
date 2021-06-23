"""Helper for extracting meta information from pornhub."""
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from sqlalchemy.orm.scoping import scoped_session

from pornhub.core import logger
from pornhub.download import download_video, get_soup
from pornhub.helper import check_logged_out, get_clip_path, link_duplicate
from pornhub.models import Clip, User
from pornhub.models.user import User


def download_user_videos(session: scoped_session, user: User) -> bool:
    """Download all videos of a user."""
    video_viewkeys = get_user_video_viewkeys(user)

    # Try to get all uploaded videos
    video_upload_viewkeys = get_video_upload_viewkeys(user)
    # If that doesn't work, try to get all public uploaded videos
    if len(video_upload_viewkeys) == 0:
        video_upload_viewkeys = get_video_upload_viewkeys(user, True)

    viewkeys = set(video_viewkeys + video_upload_viewkeys)

    if len(viewkeys) == 0:
        logger.error(f"Found 0 videos for user {user.key}. Aborting")
        sys.exit(1)

    full_success = True

    logger.info(f"Found {len(viewkeys)} videos.")
    for viewkey in viewkeys:
        clip = Clip.get_or_create(session, viewkey, user)

        # The clip has already been downloaded, skip it.
        if clip.completed:
            if clip.title is not None and clip.extension is not None:
                target_path = get_clip_path(user.name, clip.title, clip.extension)
                link_duplicate(clip, target_path)

            if clip.user is None:
                clip.user = user
                session.commit()

            continue

        info = download_video(viewkey, user.name)
        if info is not None:
            clip.title = info["title"]
            clip.tags = info["tags"]
            clip.cartegories = info["categories"]
            clip.completed = True
            clip.user = user
            clip.location = info["out_path"]
            clip.extension = info["ext"]

            logger.info(f"New video: {clip.title}")
        else:
            full_success = False

        session.commit()
        time.sleep(20)

    return full_success


def get_user_info(key: str) -> Dict[str, str]:
    """Get all necessary user information."""
    user_type, url, soup = get_user_type_and_url(key)
    name = get_user_name_from_soup(soup)
    if name is None:
        logger.error(f"Couldn't get user info for {key}")
        sys.exit(1)

    name = name.strip()
    name = name.replace(" ", "_")
    name = re.sub(r"[\W]+", "_", name)

    return {
        "type": user_type,
        "url": url,
        "name": name,
    }


def get_user_type_and_url(key: str) -> Tuple[str, str, BeautifulSoup]:
    """Detect the user type and the respective url for this user."""
    possible_urls = {}
    for user_type in [User.PORNSTAR, User.MODEL, User.USER]:
        possible_urls[user_type] = get_user_video_url(user_type, key)

    for user_type, url in possible_urls.items():
        soup = get_soup(url, False)

        if soup is not None:
            return user_type, url, soup

    raise Exception(f"Couldn't detect type for user {key}")


def get_user_name_from_soup(soup: BeautifulSoup) -> Optional[str]:
    """Get the name of the user by website."""
    profileHeader = soup.find("section", {"class": "topProfileHeader"})
    if profileHeader is None:
        profileHeader = soup.find(id="topProfileHeader")

    if profileHeader is None:
        return None

    # Try to get the user name from subscription element
    div = profileHeader.find("div", {"class": "nameSubscribe"})
    if div is not None:
        h1 = div.find("h1")
        return h1.text

    # Try to get the user name  from normal profile
    div = profileHeader.find("div", {"class": "profileUserName"})
    if div is not None:
        a = div.find("a")
        return a.text

    return None


def get_user_video_url(user_type: str, key: str) -> str:
    """Compile the user videos url."""
    is_premium = os.path.exists("http_cookie_file")
    if is_premium:
        return f"https://www.pornhubpremium.com/{user_type}/{key}"

    return f"https://www.pornhub.com/{user_type}/{key}"


def get_user_video_viewkeys(user: User) -> List[Any]:
    """Scrape viewkeys from the user's user/videos route."""
    is_premium = os.path.exists("http_cookie_file")
    if is_premium:
        url = f"https://www.pornhubpremium.com/{user.user_type}/{user.key}/videos"
    else:
        url = f"https://www.pornhub.com/{user.user_type}/{user.key}/videos"

    soup = get_soup(url)
    if soup is None:
        logger.info(f"Nothing on {url}")
        return []

    pages = 1
    hasEndlessScrolling = False

    # Some sites have a navigation at the bottom
    navigation = soup.find("div", {"class": "pagination3"})
    if navigation is not None:
        children = navigation.findChildren("li", {"class": "page_number"})
        pages = len(children) + 1
    # Others have a button for "endless scrolling"
    # In that case we have to search as long as
    elif soup.find(id="moreDataBtnStream"):
        hasEndlessScrolling = True

    keys = []
    current_page = 1
    next_url = url
    while current_page <= pages:
        # Check if the next site has another "endless scrolling" button as qell
        # If that's the case, increase the counter
        if hasEndlessScrolling and soup.find(id="moreDataBtnStream"):
            pages += 1

        logger.info(f"Crawling {next_url}")
        # Users with normal video upload list
        videos = soup.find("div", {"class": "mostRecentVideosSection"})

        if videos is None:
            return []

        for video in videos.find_all("li"):
            if video.has_attr("data-video-vkey"):
                keys.append(video["data-video-vkey"])

        current_page += 1
        next_url = url + f"?page={current_page}"

        time.sleep(4)

        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys


def get_video_upload_viewkeys(user: User, public: bool = False) -> List[str]:
    """Scrape viewkeys from the user's user/videos/upload route."""
    is_premium = os.path.exists("http_cookie_file")
    if is_premium:
        url = (
            f"https://www.pornhubpremium.com/{user.user_type}/{user.key}/videos/upload"
        )
    else:
        url = f"https://www.pornhub.com/{user.user_type}/{user.key}/videos/upload"

    if public:
        if is_premium:
            url = f"https://www.pornhubpremium.com/{user.user_type}/{user.key}/videos/public"
        else:
            url = f"https://www.pornhub.com/{user.user_type}/{user.key}/videos/public"

    soup = get_soup(url)
    if soup is None:
        logger.info(f"Nothing on {url}")
        return []

    pages = 1
    hasEndlessScrolling = False

    # Some sites have a navigation at the bottom
    navigation = soup.find("div", {"class": "pagination3"})
    if navigation is not None:
        children = navigation.findChildren("li", {"class": "page_number"})
        pages = len(children) + 1
    # Others have a button for "endless scrolling"
    # In that case we have to search as long as
    elif soup.find(id="moreDataBtnStream"):
        hasEndlessScrolling = True

    keys = []
    current_page = 1
    next_url = url
    while current_page <= pages:
        # Check if the next site has another "endless scrolling" button as qell
        # If that's the case, increase the counter
        if hasEndlessScrolling and soup.find(id="moreDataBtnStream"):
            pages += 1

        logger.info(f"Crawling {next_url}")
        videoSection = soup.find("div", {"class": "videoUList"})
        pornstarVideoSection = soup.find(id="pornstarsVideoSection")
        claimedUploadedVideoSection = soup.find(id="claimedUploadedVideoSection")

        # Users with normal video upload list
        if videoSection is not None:
            videos = videoSection.find(id="moreData")
        # Users with pornstarVideoSection
        elif pornstarVideoSection is not None:
            videos = pornstarVideoSection
        # Dunno what this is
        elif claimedUploadedVideoSection is not None:
            videos = claimedUploadedVideoSection
        else:
            logger.error(f"Couldn't find video section on {next_url}. Did we log out?")
            if check_logged_out(soup):
                sys.exit(1)
            return []

        for video in videos.find_all("li"):
            if video.has_attr("data-video-vkey"):
                keys.append(video["data-video-vkey"])

        current_page += 1
        next_url = url + f"?page={current_page}"

        time.sleep(4)

        soup = get_soup(next_url)
        # We couldn't get the next url.
        if soup is None:
            break

    return keys
