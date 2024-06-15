import os
import sys
import unittest
from unittest.mock import Mock
import pytest
from requests import patch

from src.logger import logging
from src.exception import AppException
from src.components.data_ingestion import DataIngestion
from src.components.feaature_engineering import FeatureEngineering
from src.components.data_validation import DataValidation
from src.components.model_trainer import ModelTrainer

from src.entity.config_entity import (DataIngestionConfig, DataValidationConfig, ModelTrainerConfig, FeatureEngineeringConfig)

from src.entity.artifacts_entity import (DataIngestionArtifact, DataValidationArtifact, ModelTrainerArtifact, FeatureEngineeringArtifact)
from src.pipeline.training_pipeline import TrainingPipeline

class TestTrainingPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = TrainingPipeline()
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.feature_engineering_config = FeatureEngineeringConfig()
        self.model_trainer_config = ModelTrainerConfig()
        self.valid_config =  DataIngestionConfig(attribute1='value1', attribute2='value2')
        self.invalid_config =  DataIngestionConfig(attribute1='value1', attribute2='value2', attribute3='value3')
        self.data_validation_artifact = DataValidationArtifact()

    def test_start_data_ingestion_valid_config(self):

        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.data_ingestion_config = DataIngestionConfig(self.valid_config)
    
        # Act
        data_ingestion_artifact = training_pipeline.start_data_ingestion()
    
        # Assert
        assert isinstance(data_ingestion_artifact, DataIngestionArtifact)
        assert data_ingestion_artifact.success == True
    
    def test_start_data_ingestion_invalid_config(self):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.data_ingestion_config = DataIngestionConfig(self.invalid_config)
    
        # Act and Assert
        with pytest.raises(AppException):
            training_pipeline.start_data_ingestion()
    
    def test_start_data_ingestion_exception(self):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.data_ingestion_config = DataIngestionConfig(self.valid_config)
        training_pipeline.data_ingestion = Mock(side_effect=Exception('Data ingestion failed'))
    
        # Act and Assert
        with pytest.raises(AppException):
            training_pipeline.start_data_ingestion()
    
    def test_start_data_ingestion_logging(self):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.data_ingestion_config = DataIngestionConfig(self.valid_config)
        mock_logger = Mock()
        logging.info = mock_logger
    
        # Act
        training_pipeline.start_data_ingestion()
    
        # Assert
        mock_logger.assert_any_call('Starting data ingestion')
        mock_logger.assert_any_call('Data Ingestion in the Training Class')
    
    def test_start_data_ingestion_invalid_artifact(self):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.data_ingestion_config = DataIngestionConfig(self.valid_config)
        training_pipeline.data_ingestion = Mock(return_value=DataIngestionArtifact(success=False))
    
        # Act and Assert
        with pytest.raises(AppException):
            training_pipeline.start_data_ingestion()
        
    def test_data_validation_receives_correct_artifact(mocker):
        # Arrange
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = mocker.MagicMock()
        expected_data_validation_artifact = mocker.MagicMock()
    
        # Mock the initiate_validation method of DataValidation class
        mocker.patch('src.components.data_validation.DataValidation.initiate_validation', return_value=expected_data_validation_artifact)
    
        # Act
        actual_data_validation_artifact = training_pipeline.start_data_validation(data_ingestion_artifact)
    
        # Assert
        assert actual_data_validation_artifact == expected_data_validation_artifact
        data_validation_initiate_validation_mock = mocker.patch.object(training_pipeline, 'data_validation').initiate_validation
        data_validation_initiate_validation_mock.assert_called_once_with()
    
    def test_data_validation_raises_app_exception_on_error(mocker):
        # Arrange
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = mocker.MagicMock()
        error_message = "An error occurred during data validation"
    
        # Mock the initiate_validation method of DataValidation class to raise an exception
        mocker.patch('src.components.data_validation.DataValidation.initiate_validation', side_effect=Exception(error_message))
    
        # Act and Assert
        with pytest.raises(AppException) as e:
            training_pipeline.start_data_validation(data_ingestion_artifact)
    
        assert str(e.value) == error_message
    
    def test_data_validation_logs_correct_information(mocker):
        # Arrange
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = mocker.MagicMock()
    
        # Act
        training_pipeline.start_data_validation(data_ingestion_artifact)
    
        # Assert
        logging_info_mock = mocker.patch.object(logging, 'info')
        logging_info_mock.assert_any_call('Starting data validation')
        logging_info_mock.assert_any_call('Data Validation in the Training Class')
    
    def test_data_validation_returns_expected_artifact(mocker):
        # Arrange
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = mocker.MagicMock()
        expected_data_validation_artifact = mocker.MagicMock()
    
        # Mock the initiate_validation method of DataValidation class
        mocker.patch('src.components.data_validation.DataValidation.initiate_validation', return_value=expected_data_validation_artifact)
    
        # Act
        actual_data_validation_artifact = training_pipeline.start_data_validation(data_ingestion_artifact)
    
        # Assert
        assert actual_data_validation_artifact == expected_data_validation_artifact
    
    def test_data_validation_does_not_call_initiate_model_trainer_if_validation_fails(mocker):
        # Arrange
        training_pipeline = TrainingPipeline()
        data_ingestion_artifact = mocker.MagicMock()
        data_validation_artifact = mocker.MagicMock(validation_status=False, data_status=False)
    
        # Mock the initiate_validation method of DataValidation class
        mocker.patch('src.components.data_validation.DataValidation.initiate_validation', return_value=data_validation_artifact)
    
        # Act
        with pytest.raises(Exception) as e:
            training_pipeline.run_pipeline()
    
        # Assert
        assert str(e.value) == 'Data is not valid'
        initiate_model_trainer_mock = mocker.patch.object(training_pipeline, 'start_model_trainer')
        initiate_model_trainer_mock.assert_not_called()

    def test_feature_engineering_success(self):
        # Mock the FeatureEngineering class and its method
        feature_engineering_mock = Mock(spec=FeatureEngineering)
        feature_engineering_mock.initiate_feature_engineering.return_value = "feature_engineering_artifact"
        self.pipeline.start_feature_engineering = Mock(return_value="feature_engineering_artifact")

        result = self.pipeline.start_feature_engineering(self.data_validation_artifact)
        self.assertEqual(result, "feature_engineering_artifact")

    def test_feature_engineering_exception(self):
        # Mock the FeatureEngineering class and its method to raise an exception
        feature_engineering_mock = Mock(spec=FeatureEngineering)
        feature_engineering_mock.initiate_feature_engineering.side_effect = Exception("Test exception")
        self.pipeline.start_feature_engineering = Mock(side_effect=Exception("Test exception"))

        with self.assertRaises(AppException):
            self.pipeline.start_feature_engineering(self.data_validation_artifact)

    def test_feature_engineering_logging(self):
        # Mock the logging module to check if the correct log message is being logged
        logging_mock = Mock(spec=logging)
        logging_mock.info.assert_called_once_with('Starting feature engineering')
        self.pipeline.start_feature_engineering(self.data_validation_artifact)

    def test_feature_engineering_config(self):
        # Test if the feature engineering config is being used correctly
        self.pipeline.feature_engineering_config = "test_config"
        with self.assertRaises(AppException):
            self.pipeline.start_feature_engineering(self.data_validation_artifact)

    def test_feature_engineering_data_validation_artifact(self):
        # Test if the data validation artifact is being used correctly
        self.data_validation_artifact = None
        with self.assertRaises(AppException):
            self.pipeline.start_feature_engineering(self.data_validation_artifact)

    def test_model_trainer_success(self):
        # Mock the ModelTrainer class and its method
        model_trainer_mock = Mock(spec=ModelTrainer)
        model_trainer_mock.initiate_model_training.return_value = "model_trainer_artifact"
        self.pipeline.start_model_trainer = Mock(return_value="model_trainer_artifact")
        
    @patch('src.logger.logging.info')
    def test_start_model_trainer_logs_correct_message(self, mock_logging_info):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.model_trainer_config = ModelTrainerConfig()

        # Act
        training_pipeline.start_model_trainer()

        # Assert
        mock_logging_info.assert_called_once_with("Starting model Trainer")
    
    @patch('src.logger.logging.info')
    @patch('src.model_trainer.ModelTrainer.initiate_model_trainer')
    def test_start_model_trainer_raises_app_exception_on_error(self, mock_initiate_model_trainer, mock_logging_info):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.model_trainer_config = ModelTrainerConfig()
        mock_initiate_model_trainer.side_effect = Exception("An error occurred during model training")

        # Act
        with self.assertRaises(AppException):
            training_pipeline.start_model_trainer()

        # Assert
        mock_logging_info.assert_called_once_with("Starting model Trainer")
    
    @patch('src.logger.logging.info')
    @patch('src.model_trainer.ModelTrainer.initiate_model_trainer')
    def test_start_model_trainer_returns_model_trainer_artifact(self, mock_initiate_model_trainer, mock_logging_info):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.model_trainer_config = ModelTrainerConfig()
        mock_initiate_model_trainer.return_value = ModelTrainerArtifact()

        # Act
        model_trainer_artifact = training_pipeline.start_model_trainer()

        # Assert
        mock_logging_info.assert_called_once_with("Starting model Trainer")
        self.assertIsInstance(model_trainer_artifact, ModelTrainerArtifact)

    @patch('src.logger.logging.info')
    @patch('src.model_trainer.ModelTrainer.initiate_model_trainer')
    def test_start_model_trainer_does_not_log_on_error(self, mock_initiate_model_trainer, mock_logging_info):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.model_trainer_config = ModelTrainerConfig()
        mock_initiate_model_trainer.side_effect = Exception("An error occurred during model training")

        # Act
        with self.assertRaises(AppException):
            training_pipeline.start_model_trainer()

        # Assert
        mock_logging_info.assert_called_once_with("Starting model Trainer")
        mock_logging_info.assert_not_called()
    
    @patch('src.logger.logging.info')
    @patch('src.model_trainer.ModelTrainer.initiate_model_trainer')
    def test_start_model_trainer_returns_none_on_error(self, mock_initiate_model_trainer, mock_logging_info):
        # Arrange
        training_pipeline = TrainingPipeline()
        training_pipeline.model_trainer_config = ModelTrainerConfig()
        mock_initiate_model_trainer.side_effect = Exception("An error occurred during model training")

        # Act
        with self.assertRaises(AppException):
            model_trainer_artifact = training_pipeline.start_model_trainer()

        # Assert
        mock_logging_info.assert_called_once_with("Starting model Trainer")
        self.assertIsNone(model_trainer_artifact)




if __name__ == '__main__':
    unittest.main()

