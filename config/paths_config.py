import os

RAW_DIR = "artifacts/raw"
RAW_FILE_PATH = os.path.join(RAW_DIR,"raw.csv")

# Processed data directory
PROCESSED_DIR = os.path.join(ARTIFACTS_DIR, "processed_data")
def get_processed_file_path(filename):
    return os.path.join(PROCESSED_DIR, filename)

CONFIG_PATH = "config/config.yaml"


