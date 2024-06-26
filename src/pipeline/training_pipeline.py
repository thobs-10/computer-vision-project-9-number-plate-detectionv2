import os
import sys

from src.logger import logging
from src.exception import AppException
from src.components.data_ingestion import DataIngestion
from src.components.feaature_engineering import FeatureEngineering
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer

from src.entity.config_entity import (DataIngestionConfig, DataValidationConfig, ModelTrainerConfig, FeatureEngineeringConfig)

from src.entity.artifacts_entity import (DataIngestionArtifact, DataValidationArtifact, ModelTrainerArtifact, FeatureEngineeringArtifact)

class TrainingPipeline:
    def __init__(self) -> None:
        # self.data_ingestion_config = DataIngestionConfig
        self.data_ingestion_config = DataIngestionConfig
        self.data_validation_config = DataValidationConfig
        self.feature_engineering_config = FeatureEngineeringConfig
        self.model_trainer_config = ModelTrainerConfig

    def start_data_ingestion(self) -> DataIngestionArtifact:
        """
        This function initiates the data ingestion process.

        Parameters:
        self (TrainingPipeline): The instance of the TrainingPipeline class.

        Returns:
        DataIngestionArtifact: The artifact resulting from the data ingestion process.

        Raises:
        AppException: If an error occurs during the data ingestion process.
        """
        try:
            logging.info('Starting data ingestion')
            logging.info('Data Ingestion in the Training Class')
            data_ingestion = DataIngestion(self.data_ingestion_config)
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
            return data_ingestion_artifact
        except Exception as e:
            raise AppException(e, sys)
    
    def start_data_validation(self, data_ingestion_artifact : DataIngestionArtifact) -> DataValidationArtifact:
        """
        This function initiates the data validation process.

        Parameters:
        self (TrainingPipeline): The instance of the TrainingPipeline class.
        data_ingestion_artifact (DataIngestionArtifact): The artifact resulting from the data ingestion process.

        Returns:
        DataValidationArtifact: The artifact resulting from the data validation process.

        Raises:
        AppException: If an error occurs during the data validation process.
        """
        try:
            logging.info('Starting data validation')
            logging.info('Data Validation in the Training Class')
            data_validation = DataValidation(data_ingestion_artifact, self.data_validation_config)
            data_validation_artifact = data_validation.initiate_validation()
            return data_validation_artifact
        except Exception as e:
            raise AppException(e, sys)
    
    def start_feature_engineering(self, data_validation_artifact: DataValidationArtifact) -> FeatureEngineeringArtifact:
        """
        This function initiates the feature engineering process.

        Parameters:
        self (TrainingPipeline): The instance of the TrainingPipeline class.
        data_validation_artifact (DataValidationArtifact): The artifact resulting from the data validation process.

        Returns:
        FeatureEngineeringArtifact: The artifact resulting from the feature engineering process.

        Raises:
        AppException: If an error occurs during the feature engineering process.
        """
        try:
            logging.info('Starting feature engineering')
            feature_engineering = FeatureEngineering(self.feature_engineering_config, data_validation_artifact)
            feature_engineering_artifact = feature_engineering.initiate_feature_engineering()
            return feature_engineering_artifact
        except Exception as e:
            raise AppException(e, sys)
        
    
    def start_model_trainer(self)-> ModelTrainerArtifact:
        """
        This function initiates the model training process.

        Parameters:
        self (TrainingPipeline): The instance of the TrainingPipeline class.

        Returns:
        ModelTrainerArtifact: The artifact resulting from the model training process.

        Raises:
        AppException: If an error occurs during the model training process.
        """
        logging.info("Starting model Trainer")
        try:
            model_trainer = ModelTrainer(model_trainer_config= self.model_trainer_config)
            model_trainer_artifact = model_trainer.initiate_model_trainer()
            return model_trainer_artifact
        except Exception as e:
            raise AppException(e, sys)
    
    def run_pipeline(self)-> None:
        """
        This function initiates the entire training pipeline.

        Parameters:
        self (TrainingPipeline): The instance of the TrainingPipeline class.

        Returns:
        None: This function does not return any value.

        Raises:
        AppException: If an error occurs during the pipeline execution.
        Exception: If the data validation fails.
        """
        try:
            logging.info('Starting pipeline')
            data_ingestion_artifact = self.start_data_ingestion()
            data_validation_artifact = self.start_data_validation(data_ingestion_artifact)
            if data_validation_artifact.validation_status == True and data_validation_artifact.data_status == True:
                model_trainer_artifact = self.start_model_trainer()
            else:
                raise Exception('Data is not valid')
            
            
        except Exception as e:
            raise AppException(e, sys)
        
