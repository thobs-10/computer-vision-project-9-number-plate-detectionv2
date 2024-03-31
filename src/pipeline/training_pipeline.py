import os
import sys

from src.logger import logging
from src.exception import AppException
from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation

from src.entity.config_entity import (DataIngestionConfig, DataValidationConfig)

from src.entity.artifacts_entity import (DataIngestionArtifact, DataValidationArtifact)

class TrainingPipeline:
    def __init__(self) -> None:
        # self.data_ingestion_config = DataIngestionConfig
        self.data_ingestion_config = DataIngestionConfig
        self.data_validation_config = DataValidationConfig


    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logging.info('Starting data ingestion')
            logging.info('Data Ingestion in the Training Class')
            data_ingestion = DataIngestion(self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact
        except Exception as e:
            raise AppException(e, sys)
    
    def start_data_validation(self, data_ingestion_artifact : DataIngestionArtifact) -> DataValidationArtifact:
        try:
            logging.info('Starting data validation')
            logging.info('Data Validation in the Training Class')
            data_validation = DataValidation(data_ingestion_artifact, self.data_validation_config)
            data_validation_artifact = data_validation.initiate_validation()
            return data_validation_artifact
        except Exception as e:
            raise AppException(e, sys)
        
    
    def run_pipeline(self)-> None:
        try:
            logging.info('Starting pipeline')
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact)
            
        except Exception as e:
            raise AppException(e, sys)
        
