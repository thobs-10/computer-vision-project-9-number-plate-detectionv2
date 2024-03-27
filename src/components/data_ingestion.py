import os
import sys
import zipfile
import gdown

from src.logger import logging
from src.exception import AppException
from src.entity.artifacts_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig = DataIngestionConfig()):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise AppException(e, sys)
    
    def download_data_from_url(self) -> str:
        try:
            logging.info('Downloading data from url')
            dataset_url = self.data_ingestion_config.data_download_url
            zip_download_dir = self.data_ingestion_config.data_ingestion_dir
            # make a folder
            os.makedirs(zip_download_dir, exist_ok=True)
            data_file_name = 'data.zip'
            zip_file_path = os.path.join(zip_download_dir, data_file_name)
            logging.info(f'Downloading file: {zip_file_path} from {dataset_url}')

            file_id = dataset_url.split('/')[-2]
            prefix = ''
            gdown.download(prefix+file_id, zip_file_path)
            logging.info(f'Downloaded file: {zip_file_path}')


            return zip_file_path
        except Exception as e:
            raise AppException(e, sys)

    def extract_zip_file(self, zip_file_path:str)-> str:
        
        try:
            logging.info('Extracting zip file')
            feature_store_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(feature_store_path, exist_ok= True)
            with zipfile.ZipFile(zip_file_path, 'r') as zipped_feature_store:
                zipped_feature_store.extractall(feature_store_path)

            logging.info(f'Extracted file: {feature_store_path}')
            return feature_store_path
        except Exception as e:
            raise AppException(e, sys)
    
    def initiate_data_ingestion(self) -> DataIngestionArtifact:

        zip_file_path = self.download_data_from_url()
        feature_store_path = self.extract_zip_file(zip_file_path)

        data_ingestion_artifact = DataIngestionArtifact(
            zip_file_path=zip_file_path,
            feature_store_path=feature_store_path
        )
        return data_ingestion_artifact
    
