import os
import unittest
import zipfile
from unittest.mock import patch
import pytest
import requests
from src.entity.artifacts_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig
from src.components.data_ingestion import DataIngestion
from src.exception import AppException

class Unittest(unittest.TestCase):

    def setUp(self):
        self.data_ingestion_config = DataIngestionConfig(
            feature_store_file_path='test_feature_store'
        )
        self.data_ingestion = DataIngestion(self.data_ingestion_config)

    def test_download_data_from_url_valid_url_and_directory():
        # Arrange
        data_ingestion_config = DataIngestionConfig(
            data_download_url='https://example.com/dataset.zip',
            data_ingestion_dir='/tmp/data'
        )
        data_ingestion = DataIngestion(data_ingestion_config)
    
        # Act
        zip_file_path = data_ingestion.download_data_from_url()
    
        # Assert
        expected_zip_file_path = '/tmp/data/data.zip'
        assert zip_file_path == expected_zip_file_path

    def test_download_data_from_url_invalid_url():
        # Arrange
        data_ingestion_config = DataIngestionConfig(
            data_download_url='https://example.com/invalid_dataset.zip',
            data_ingestion_dir='/tmp/data'
        )
        data_ingestion = DataIngestion(data_ingestion_config)
    
        # Act and Assert
        with pytest.raises(AppException):
            data_ingestion.download_data_from_url()
    def test_download_data_from_url_non_existent_directory():
        # Arrange
        data_ingestion_config = DataIngestionConfig(
            data_download_url='https://example.com/dataset.zip',
            data_ingestion_dir='/tmp/non_existent_directory'
        )
        data_ingestion = DataIngestion(data_ingestion_config)
    
        # Act and Assert
        with pytest.raises(FileNotFoundError):
            data_ingestion.download_data_from_url()

    def test_download_data_from_url_non_zip_file():
        # Arrange
        data_ingestion_config = DataIngestionConfig(
            data_download_url='https://example.com/dataset.txt',
            data_ingestion_dir='/tmp/data'
        )
        data_ingestion = DataIngestion(data_ingestion_config)
    
        # Act and Assert
        with pytest.raises(ValueError):
            data_ingestion.download_data_from_url()
    
    def test_download_data_from_url_large_file():
        # Arrange
        data_ingestion_config = DataIngestionConfig(
            data_download_url='https://example.com/large_dataset.zip',
            data_ingestion_dir='/tmp/data'
        )
        data_ingestion = DataIngestion(data_ingestion_config)
    
        # Act
        zip_file_path = data_ingestion.download_data_from_url()
    
        # Assert
        expected_zip_file_path = '/tmp/data/data.zip'
        assert zip_file_path == expected_zip_file_path

    def test_extract_zip_file_success(self):
        # Create a temporary zip file with some contents
        zip_file_path = 'test_data.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipped_file:
            zipped_file.writestr('test_file.txt', 'This is a test file.')

        # Call the extract_zip_file method
        feature_store_path = self.data_ingestion.extract_zip_file(zip_file_path)

        # Verify that the zip file was extracted correctly
        self.assertTrue(os.path.exists(feature_store_path))
        self.assertTrue(os.path.exists(os.path.join(feature_store_path, 'test_file.txt')))

        # Clean up the temporary files
        os.remove(zip_file_path)
        os.rmdir(feature_store_path)
    
    def test_extract_zip_file_no_contents(self):
        # Create a temporary zip file with no contents
        zip_file_path = 'test_data_no_contents.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipped_file:
            pass

        # Call the extract_zip_file method
        feature_store_path = self.data_ingestion.extract_zip_file(zip_file_path)

        # Verify that the zip file was extracted correctly
        self.assertTrue(os.path.exists(feature_store_path))
        self.assertFalse(os.listdir(feature_store_path))

        # Clean up the temporary files
        os.remove(zip_file_path)
        os.rmdir(feature_store_path)

    def test_extract_zip_file_nonexistent_file(self):
        # Provide a nonexistent zip file path
        zip_file_path = 'nonexistent_file.zip'

        # Call the extract_zip_file method and expect an AppException
        with self.assertRaises(AppException):
            self.data_ingestion.extract_zip_file(zip_file_path)


    def test_extract_zip_file_invalid_zip_file(self):
        # Provide an invalid zip file path
        zip_file_path = 'invalid_file.txt'

        # Call the extract_zip_file method and expect an AppException
        with self.assertRaises(AppException):
            self.data_ingestion.extract_zip_file(zip_file_path)

    def test_extract_zip_file_permission_error(self):
        # Create a temporary zip file
        zip_file_path = 'test_data.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipped_file:
            zipped_file.writestr('test_file.txt', 'This is a test file.')

        # Make the feature store directory unwritable
        feature_store_path = self.data_ingestion_config.feature_store_file_path
        os.chmod(feature_store_path, 0o444)

        # Call the extract_zip_file method and expect an AppException
        with self.assertRaises(AppException):
            self.data_ingestion.extract_zip_file(zip_file_path)

        # Clean up the temporary files
        os.remove(zip_file_path)
        os.chmod(feature_store_path, 0o755)

    def test_initiate_data_ingestion_empty_url():
        # Create a mock DataIngestionConfig object with an empty URL
        config = DataIngestionConfig(data_download_url='')
    
        # Create a DataIngestion object with the mock config
        data_ingestion = DataIngestion(data_ingestion_config=config)
    
        # Expect a ValueError to be raised when initiating data ingestion
        with pytest.raises(ValueError) as e:
            data_ingestion.initiate_data_ingestion()
    
        # Assert that the error message contains the expected information
        assert str(e.value) == "Invalid URL: ''"
    
    def test_initiate_data_ingestion_non_existent_url():
        # Create a mock DataIngestionConfig object with a non-existent URL
        config = DataIngestionConfig(data_download_url='https://example.com/nonexistent.zip')
    
        # Create a DataIngestion object with the mock config
        data_ingestion = DataIngestion(data_ingestion_config=config)
    
        # Expect a requests.exceptions.HTTPError to be raised when initiating data ingestion
        with pytest.raises(requests.exceptions.HTTPError) as e:
            data_ingestion.initiate_data_ingestion()
    
        # Assert that the error message contains the expected information
        assert str(e.value) == "404 Client Error: Not Found for url: https://example.com/nonexistent.zip"
    
    def test_initiate_data_ingestion_unsupported_file_format():
        # Create a mock DataIngestionConfig object with a URL pointing to a .txt file
        config = DataIngestionConfig(data_download_url='https://example.com/data.txt')
    
        # Create a DataIngestion object with the mock config
        data_ingestion = DataIngestion(data_ingestion_config=config)
    
        # Expect a ValueError to be raised when initiating data ingestion
        with pytest.raises(ValueError) as e:
            data_ingestion.initiate_data_ingestion()
    
        # Assert that the error message contains the expected information
        assert str(e.value) == "Unsupported file format: .txt"
    
    def test_initiate_data_ingestion_redirect_to_unsupported_file_format():
        # Create a mock DataIngestionConfig object with a URL that redirects to a .txt file
        config = DataIngestionConfig(data_download_url='https://example.com/redirect.zip')
    
        # Create a DataIngestion object with the mock config
        data_ingestion = DataIngestion(data_ingestion_config=config)
    
        # Expect a ValueError to be raised when initiating data ingestion
        with pytest.raises(ValueError) as e:
            data_ingestion.initiate_data_ingestion()
    
        # Assert that the error message contains the expected information
        assert str(e.value) == "Unsupported file format: .txt"
    
    def test_initiate_data_ingestion_non_zip_file():
        # Create a mock DataIngestionConfig object with a URL that returns a non-zip file
        config = DataIngestionConfig(data_download_url='https://example.com/data.txt')
    
        # Create a DataIngestion object with the mock config
        data_ingestion = DataIngestion(data_ingestion_config=config)
    
        # Expect a ValueError to be raised when initiating data ingestion
        with pytest.raises(ValueError) as e:
            data_ingestion.initiate_data_ingestion()
    
        # Assert that the error message contains the expected information
        assert str(e.value) == "Unsupported file format: .txt"

if __name__ == '__main__':
    unittest.main()
    