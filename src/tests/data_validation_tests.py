import os
import shutil
import unittest
from unittest import mock
from unittest.mock import patch
from src.logger import logging
from src.exception import AppException
from src.entity.config_entity import DataValidationConfig
from src.entity.artifacts_entity import DataIngestionArtifact
from src.components.data_validation import DataValidation


class TestDataValidation(unittest.TestCase):
    @patch('os.listdir')
    @patch('os.path.getsize')
    def test_validate_data_within_files_non_empty(self, mock_getsize, mock_listdir):
        # Mock data
        feature_store_path = '/path/to/feature_store'
        data_folders = ['folder1', 'folder2']
        mock_listdir.side_effect = [[data_folders], ['file1', 'file2']]
        mock_getsize.return_value = 1024  # Non-empty directory

        # Create DataIngestionArtifact and DataValidationConfig objects
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path=feature_store_path)
        data_validation_config = DataValidationConfig()

        # Create DataValidation object
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        # Call the method and assert the result
        result = data_validation.validate_data_within_files()
        self.assertTrue(result)

        # Assert that appropriate messages are logged
        expected_logs = [
            f"The directory {data_folders[0]} is not empty",
            f"The directory {data_folders[1]} is not empty"
        ]
        self.assertEqual(logging.info.call_count, len(expected_logs))
        for call_args in logging.info.call_args_list:
            self.assertIn(call_args[0][0], expected_logs)

    
    @patch('os.listdir')
    @patch('os.path.getsize')
    def test_validate_data_within_files_empty(self, mock_getsize, mock_listdir):
        # Mock data
        feature_store_path = '/path/to/feature_store'
        data_folders = ['folder1', 'folder2']
        mock_listdir.side_effect = [[data_folders], ['file1', 'file2']]
        mock_getsize.return_value = 0  # Empty directory

        # Create DataIngestionArtifact and DataValidationConfig objects
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path=feature_store_path)
        data_validation_config = DataValidationConfig()

        # Create DataValidation object
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        # Call the method and assert the result
        result = data_validation.validate_data_within_files()
        self.assertFalse(result)

        # Assert that appropriate messages are logged
        expected_logs = [
            f"The directory {data_folders[0]} is empty",
            f"The directory {data_folders[1]} is empty"
        ]
        self.assertEqual(logging.info.call_count, len(expected_logs))
        for call_args in logging.info.call_args_list:
            self.assertIn(call_args[0][0], expected_logs)
    patch('os.listdir')
    def test_validate_data_within_files_no_directories(self, mock_listdir):
        # Mock data
        feature_store_path = '/path/to/feature_store'
        mock_listdir.return_value = ['file1', 'file2']  # No directories

        # Create DataIngestionArtifact and DataValidationConfig objects
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path=feature_store_path)
        data_validation_config = DataValidationConfig()

        # Create DataValidation object
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        # Call the method and assert the result
        result = data_validation.validate_data_within_files()
        self.assertFalse(result)

        # Assert that appropriate message is logged
        expected_log = "The directory has zero contents"
        self.assertEqual(logging.info.call_count, 1)
        self.assertEqual(logging.info.call_args[0][0], expected_log)
    
    @patch('os.listdir')
    @patch('os.path.getsize')
    def test_validate_data_within_files_exception(self, mock_getsize, mock_listdir):
        # Mock data
        feature_store_path = '/path/to/feature_store'
        data_folders = ['folder1', 'folder2']
        mock_listdir.side_effect = [[data_folders], ['file1', 'file2']]
        mock_getsize.side_effect = OSError("Error occurred")  # Exception

        # Create DataIngestionArtifact and DataValidationConfig objects
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path=feature_store_path)
        data_validation_config = DataValidationConfig()

        # Create DataValidation object
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        # Call the method and assert the exception is raised
        with self.assertRaises(AppException):
            data_validation.validate_data_within_files()
    
    @patch('os.listdir')
    @patch('os.path.getsize')
    def test_validate_data_within_files_single_directory(self, mock_getsize, mock_listdir):
        # Mock data
        feature_store_path = '/path/to/feature_store'
        data_folders = ['folder1']
        mock_listdir.side_effect = [[data_folders], ['file1', 'file2']]
        mock_getsize.return_value = 1024  # Non-empty directory

        # Create DataIngestionArtifact and DataValidationConfig objects
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path=feature_store_path)
        data_validation_config = DataValidationConfig()

        # Create DataValidation object
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        # Call the method and assert the result
        result = data_validation.validate_data_within_files()
        self.assertTrue(result)

        # Assert that appropriate message is logged
        expected_log = f"The directory {data_folders[0]} is not empty"
        self.assertEqual(logging.info.call_count, 1)
        self.assertEqual(logging.info.call_args[0][0], expected_log)
    
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = 'test_data_validation'
        os.makedirs(self.test_dir, exist_ok=True)

        # Create a temporary file for testing
        self.test_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(self.test_file, 'w') as f:
            f.write('Test data')

        # Create a temporary directory within the test file
        self.test_sub_dir = os.path.join(self.test_dir, 'test_sub_dir')
        os.makedirs(self.test_sub_dir, exist_ok=True)

        # Create an empty file within the test sub directory
        self.empty_file = os.path.join(self.test_sub_dir, 'empty_file.txt')
        open(self.empty_file, 'a').close()

        # Create a DataIngestionArtifact object for testing
        self.data_ingestion_artifact = DataIngestionArtifact(
            feature_store_path=self.test_dir,
            data_zip_file_path='test_data.zip'
        )

        # Create a DataValidationConfig object for testing
        self.data_validation_config = DataValidationConfig(
            required_file_list=['test_file.txt'],
            data_validation_dir='test_validation_dir'
        )

        # Create a DataValidation object for testing
        self.data_validation = DataValidation(
            data_ingestion_artifact=self.data_ingestion_artifact,
            data_validation_config=self.data_validation_config
        )

    def tearDown(self):
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_validate_data_within_files_returns_false_when_empty_directory(self):
        # Call the validate_data_within_files method
        result = self.data_validation.validate_data_within_files()

        # Assert that the method returns False
        self.assertFalse(result)

    def test_validate_all_files_valid_input():
        # Arrange
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path='valid_path')
        data_validation_config = DataValidationConfig(required_file_list=['file1', 'file2'])
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    
        # Act
        result = data_validation.validate_all_files()
    
        # Assert
        assert result is not None, "Expected a boolean value"
        assert isinstance(result, bool), "Expected a boolean value"
    
    def test_validate_all_files_empty_feature_store_path():
        # Arrange
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path='')
        data_validation_config = DataValidationConfig(required_file_list=['file1', 'file2'])
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    
        # Act
        result = data_validation.validate_all_files()
    
        # Assert
        assert result is None, "Expected None when feature store path is empty"

    def test_validate_all_files_non_existent_feature_store_path():
        # Arrange
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path='non_existent_path')
        data_validation_config = DataValidationConfig(required_file_list=['file1', 'file2'])
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    
        # Act
        result = data_validation.validate_all_files()
    
        # Assert
        assert result is None, "Expected None when feature store path does not exist"
    
    def test_validate_all_files_unexpected_exception():
        # Arrange
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path='valid_path')
        data_validation_config = DataValidationConfig(required_file_list=['file1', 'file2'])
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    
        # Mock the os.listdir function to raise an exception
        with mock.patch('os.listdir', side_effect=Exception('Unexpected error')):
            # Act
            try:
                data_validation.validate_all_files()
                assert False, "Expected an AppException to be raised"
            except AppException as e:
                # Assert
                assert str(e) == "Unexpected error", "Expected the AppException to contain the correct error message"
            
        
    def test_validate_all_files_required_file_missing():
        # Arrange
        data_ingestion_artifact = DataIngestionArtifact(feature_store_path='valid_path')
        data_validation_config = DataValidationConfig(required_file_list=['file1', 'file2'])
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
    
        # Mock the os.listdir function to return only one file
        with mock.patch('os.listdir', return_value=['file1']):
            # Act
            result = data_validation.validate_all_files()
    
            # Assert
            assert result is False, "Expected validation status to be False when a required file is missing"
        
    

if __name__ == '__main__':
    unittest.main()
