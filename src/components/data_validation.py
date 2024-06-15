import os,sys
import shutil
from src.logger import logging
from src.exception import AppException
from src.entity.config_entity import DataValidationConfig
from src.entity.artifacts_entity import (DataIngestionArtifact,
                                                 DataValidationArtifact)

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config : DataValidationConfig) -> None:
        """
        Initialize a new instance of DataValidation class.

        Parameters:
        data_ingestion_artifact (DataIngestionArtifact): The artifact resulting from data ingestion process.
        data_validation_config (DataValidationConfig): The configuration for data validation process.

        Returns:
        None: This method does not return any value.

        Raises:
        AppException: If any error occurs during the initialization process.
        """
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
        except Exception as e:
            raise AppException(e, sys)
        
    def validate_data_within_files(self)-> bool:
        """
        Validates the data within the files present in the feature store path.

        Parameters:
        self (DataValidation): The instance of the DataValidation class.

        Returns:
        bool: Returns True if all the directories within the files are not empty, else returns False.

        Raises:
        AppException: If any error occurs during the validation process.
        """
        try:
            isPresent = None
            all_files_from_ingestion = os.listdir(self.data_ingestion_artifact.feature_store_path) 
            for file in all_files_from_ingestion:
                data_folders = os.listdir(file)
                if len(data_folders) > 1:
                    for data_folder in data_folders:
                        if (os.path.getsize(data_folder) == 0):
                            logging.info(f"The directory {data_folder} is empty")
                            isPresent = False
                        else:
                            logging.info(f"The directory {data_folder} is not empty")
                            isPresent = True
                            # return isPresent
                else:
                    logging.info("The directory has zero contents")
                    isPresent = False
            return isPresent

        except Exception as e:
            raise AppException(e, sys)
        
    
    def validate_all_files(self)-> bool:
        """
        Validates all files present in the feature store path against the required file list.

        Parameters:
        self (DataValidation): The instance of the DataValidation class.

        Returns:
        bool: Returns True if all required files are present and validated, else returns False.

        Raises:
        AppException: If any error occurs during the validation process.
        """
        try:
            validation_status = None
            # Get all files from the feature store path
            all_files_from_ingestion = os.listdir(self.data_ingestion_artifact.feature_store_path)

            for file in all_files_from_ingestion:
                # Check if the file is in the required file list
                if file not in self.data_validation_config.required_file_list:
                    # If not, set validation status to False and log it
                    validation_status = False
                    os.makedirs(self.data_validation_config.data_validation_dir, exist_ok=True)
                    with open(self.data_validation_config.data_validation_dir, 'w') as f:
                        f.write(f'Validation Status: {validation_status}')
                    logging.info(f'Validation Status: {validation_status}')
                else:
                    # If yes, set validation status to True and log it
                    validation_status = True
                    # isPresent = self.validate_data_within_files(file)
                    os.makedirs(self.data_validation_config.data_validation_dir, exist_ok=True)
                    with open(self.data_validation_config.data_validation_dir, 'w') as f:
                        f.write(f'Validation Status: {validation_status}')
                    logging.info(f'Validation Status: {validation_status}')
            
            return validation_status
        except Exception as e:
            raise AppException(e, sys)
        
   

    def initiate_validation(self)-> DataValidationArtifact:

        try:
            val_status = self.validate_all_files()
            data_status = self.validate_data_within_files()
            data_validation_artifact = DataValidationArtifact(
                validation_status=val_status,
                data_status= data_status
            )        

            if val_status:
                shutil.copy(self.data_ingestion_artifact.data_zip_file_path, os.getcwd())
            
            return data_validation_artifact
        except Exception as e:
            raise AppException(e, sys)
