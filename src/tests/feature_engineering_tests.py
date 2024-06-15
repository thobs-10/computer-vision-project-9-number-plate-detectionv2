import os
import unittest
from unittest.mock import patch
from src.exception import AppException
from src.logger import logging
from src.entity.config_entity import FeatureEngineeringConfig
from src.entity.artifacts_entity import DataValidationArtifact, FeatureEngineeringArtifact
from src.components.feaature_engineering import FeatureEngineering

class TestFeatureEngineering(unittest.TestCase):
    @patch('os.path.exists')
    def test_initiate_feature_engineering_directory_exists(self, mock_exists):
        # Mock the existence of the transformed data directory
        mock_exists.return_value = True

        # Create mock objects
        feature_engineering_config = FeatureEngineeringConfig(feature_params={'width': 224, 'height': 224})
        data_validation_artifact = DataValidationArtifact(vaildated_data_path='data/valid')

        # Create an instance of FeatureEngineering
        feature_engineering = FeatureEngineering(feature_engineering_config, data_validation_artifact)

        # Call the initiate_feature_engineering method
        feature_engineering_artifact = feature_engineering.initiate_feature_engineering()

        # Assert that the method returns a FeatureEngineeringArtifact object
        self.assertIsInstance(feature_engineering_artifact, FeatureEngineeringArtifact)

        # Assert that the transformed data path is set correctly
        self.assertEqual(feature_engineering_artifact.transformed_data_path, 'artifacts/transformed_data')

        # Assert that the logging info is correct
        logging_info = logging.info.call_args_list[0][0][0]
        self.assertEqual(logging_info, 'Feature engineering completed. Transformed data saved at artifacts/transformed_data')

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_initiate_feature_engineering_directory_not_exists(self, mock_makedirs, mock_exists):
        # Mock the non-existence of the transformed data directory
        mock_exists.return_value = False

        # Create mock objects
        feature_engineering_config = FeatureEngineeringConfig(feature_params={'width': 224, 'height': 224})
        data_validation_artifact = DataValidationArtifact(vaildated_data_path='data/valid')

        # Create an instance of FeatureEngineering
        feature_engineering = FeatureEngineering(feature_engineering_config, data_validation_artifact)

        # Call the initiate_feature_engineering method
        feature_engineering_artifact = feature_engineering.initiate_feature_engineering()

        # Assert that the method returns a FeatureEngineeringArtifact object
        self.assertIsInstance(feature_engineering_artifact, FeatureEngineeringArtifact)

        # Assert that the transformed data path is set correctly
        self.assertEqual(feature_engineering_artifact.transformed_data_path, 'artifacts/transformed_data')

        # Assert that the transformed data directory is created
        mock_makedirs.assert_called_once_with('artifacts/transformed_data')

        # Assert that the logging info is correct
        logging_info = logging.info.call_args_list[0][0][0]
        self.assertEqual(logging_info, 'Feature engineering completed. Transformed data saved at artifacts/transformed_data')

    @patch('os.path.exists')
    @patch('cv2.imread')
    def test_initiate_feature_engineering_exception(self, mock_imread, mock_exists):
        # Mock the existence of the transformed data directory
        mock_exists.return_value = True

        # Mock the cv2.imread function to raise an exception
        mock_imread.side_effect = Exception('Error reading image')

        # Create mock objects
        feature_engineering_config = FeatureEngineeringConfig(feature_params={'width': 224, 'height': 224})
        data_validation_artifact = DataValidationArtifact(vaildated_data_path='data/valid')

        # Create an instance of FeatureEngineering
        feature_engineering = FeatureEngineering(feature_engineering_config, data_validation_artifact)

        # Call the initiate_feature_engineering method
        with self.assertRaises(AppException):
            feature_engineering.initiate_feature_engineering()

        # Assert that the logging error is correct
        logging_error = logging.error.call_args_list[0][0][0]
        self.assertEqual(logging_error, 'Error occurred during feature engineering: Error reading image')

    @patch('os.path.exists')
    @patch('cv2.imread')
    @patch('cv2.imwrite')
    def test_initiate_feature_engineering_success(self, mock_imwrite, mock_imread, mock_exists):
        # Mock the existence of the transformed data directory
        mock_exists.return_value = True

        # Create mock objects
        feature_engineering_config = FeatureEngineeringConfig(feature_params={'width': 224, 'height': 224})
        data_validation_artifact = DataValidationArtifact(vaildated_data_path='data/valid')

        # Create an instance of FeatureEngineering
        feature_engineering = FeatureEngineering(feature_engineering_config, data_validation_artifact)

        # Call the initiate_feature_engineering method
        feature_engineering_artifact = feature_engineering.initiate_feature_engineering()

        # Assert that the method returns a FeatureEngineeringArtifact object
        self.assertIsInstance(feature_engineering_artifact, FeatureEngineeringArtifact)

        # Assert that the transformed data path is set correctly
        self.assertEqual(feature_engineering_artifact.transformed_data_path, 'artifacts/transformed_data')

        # Assert that the transformed image is saved using cv2.imwrite
        mock_imwrite.assert_called_once()

        # Assert that the logging info is correct
        logging_info = logging.info.call_args_list[0][0][0]
        self.assertEqual(logging_info, 'Feature engineering completed. Transformed data saved at artifacts/transformed_data')

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_initiate_feature_engineering_directory_creation_error(self, mock_makedirs, mock_exists):
        # Mock the non-existence of the transformed data directory
        mock_exists.return_value = False

        # Mock the os.makedirs function to raise an exception
        mock_makedirs.side_effect = Exception('Error creating directory')

        # Create mock objects
        feature_engineering_config = FeatureEngineeringConfig(feature_params={'width': 224, 'height': 224})
        data_validation_artifact = DataValidationArtifact(vaildated_data_path='data/valid')

        # Create an instance of FeatureEngineering
        feature_engineering = FeatureEngineering(feature_engineering_config, data_validation_artifact)

        # Call the initiate_feature_engineering method
        with self.assertRaises(AppException):
            feature_engineering.initiate_feature_engineering()

        # Assert that the logging error is correct
        logging_error = logging.error.call_args_list[0][0][0]
        self.assertEqual(logging_error, 'Error occurred during feature engineering: Error creating directory')

    

if __name__ == '__main__':
    unittest.main()