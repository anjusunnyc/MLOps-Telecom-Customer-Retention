import os

ARTIFACTS_DIR = "artifacts"
RAW_DIR = os.path.join(ARTIFACTS_DIR, "raw_data")

def get_raw_file_path(filename):
    return os.path.join(RAW_DIR, filename)

CONFIG_PATH = "config/config.yaml"


