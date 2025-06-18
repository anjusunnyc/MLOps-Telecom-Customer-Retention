import os
import requests
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml


logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        
        ingestion_config = config["data_ingestion"]

        self.url = ingestion_config["file_url"]
        self.local_path = get_raw_file_path(ingestion_config["file_name"])
        os.makedirs(os.path.dirname(self.local_path), exist_ok=True)
        logger.info(f"Data ingestion started. Downloading from {self.url} to {self.local_path}")
    
    def download_csv_from_gcp(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            with open(self.local_path, "wb") as f:
                f.write(response.content)

            logger.info(f"CSV file is sucesfully downloaded")

        except Exception as e:
            logger.error("Error while downloading the csv file")
            raise CustomException("Failed to downlaod csv file ", e)
        
    
    def run(self):

        try:
            logger.info("Starting data ingestion process")

            self.download_csv_from_gcp()
            

            logger.info("Data ingestion completed sucesfully")
        
        except CustomException as ce:
            logger.error(f"CustomException : {str(ce)}")
        
        finally:
            logger.info("Data ingestion completed")

if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()

