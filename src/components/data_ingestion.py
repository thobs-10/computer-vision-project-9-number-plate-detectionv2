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
        """
    Downloads the data from the specified URL and saves it as a zip file.

    Parameters:
    self (DataIngestion): The instance of the DataIngestion class.

    Returns:
    str: The path of the downloaded zip file.

    Raises:
    AppException: If any error occurs during the download process.
        """  
        
        try:
            logging.info('Downloading data from url')
            dataset_url = self.data_ingestion_config.data_download_url
            zip_download_dir = self.data_ingestion_config.data_ingestion_dir
            # make a folder
            os.makedirs(zip_download_dir, exist_ok=True)
            data_file_name = 'data.zip'
            zip_file_path = os.path.join(zip_download_dir, data_file_name)
            logging.info(f'Downloading file: {zip_file_path} from {dataset_url}')
            # manipulating tte string url for gdown since it had some extra stuff in it.
            file_id = dataset_url.split('/')[-2]
            prefix = ''
            gdown.download(prefix+file_id, zip_file_path)
            logging.info(f'Downloaded file: {zip_file_path}')


            return zip_file_path
        except Exception as e:
            raise AppException(e, sys)

    def extract_zip_file(self, zip_file_path:str)-> str:
        """
    Extracts the contents of a zip file to a specified directory.

    Parameters:
    zip_file_path (str): The path of the zip file to be extracted.

    Returns:
    str: The path of the directory where the zip file contents are extracted.

    Raises:
    AppException: If any error occurs during the extraction process.
    """

        try:
            # Log the start of the extraction process
            logging.info('Extracting zip file')

            # Get the path of the feature store directory from the configuration
            feature_store_path = self.data_ingestion_config.feature_store_file_path

            # Create the feature store directory if it does not exist
            os.makedirs(feature_store_path, exist_ok=True)

            # Open the zip file in read mode
            with zipfile.ZipFile(zip_file_path, 'r') as zipped_feature_store:
                # Extract all files from the zip file to the feature store directory
                zipped_feature_store.extractall(feature_store_path)

            # Log the successful extraction
            logging.info(f'Extracted file: {feature_store_path}')

            # Return the path of the feature store directory
            return feature_store_path

        except Exception as e:
            # Raise an AppException with the original exception and the current stack trace
            raise AppException(e, sys)
    
    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
    Initiates the data ingestion process by downloading the data from the specified URL,
    extracting the zip file, and creating a DataIngestionArtifact object.

    Parameters:
    self (DataIngestion): The instance of the DataIngestion class.

    Returns:
    DataIngestionArtifact: An object containing the paths of the downloaded zip file and the extracted feature store.

    Raises:
    AppException: If any error occurs during the data ingestion process.
    """
        # Download the data from the specified URL
        zip_file_path = self.download_data_from_url()

        # Extract the contents of the zip file
        feature_store_path = self.extract_zip_file(zip_file_path)

        # Create a DataIngestionArtifact object with the paths of the downloaded zip file and the extracted feature store
        data_ingestion_artifact = DataIngestionArtifact(
            zip_file_path=zip_file_path,
            feature_store_path=feature_store_path
        )
        # Return the DataIngestionArtifact object
        return data_ingestion_artifact
    
