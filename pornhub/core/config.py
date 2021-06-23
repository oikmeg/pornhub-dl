"""Config values for pornhub."""
import os
import sys

import toml

default_config = {
    "sql_uri": "postgresql://localhost/pornhub",
    "location": os.path.expanduser("~/pornhub"),
}

config_path = os.path.expanduser("~/.config/pornhub_dl.toml")

if not os.path.exists(config_path):
    with open(config_path, "w") as file_descriptor:
        toml.dump(default_config, file_descriptor)
    print("Please adjust the configuration file at '~/.config/pornhub_dl.toml'")
    sys.exit(1)
else:
    config = toml.load(config_path)
