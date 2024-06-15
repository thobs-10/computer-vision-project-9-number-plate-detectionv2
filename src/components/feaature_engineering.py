import os
import sys
import cv2
import numpy as np
from src.exception import AppException
from src.logger import logging
from src.entity.config_entity import FeatureEngineeringConfig
from src.entity.artifacts_entity import  DataValidationArtifact, FeatureEngineeringArtifact

class FeatureEngineering:
    def __init__(self, feature_engineering_config: FeatureEngineeringConfig, data_validation_artifact: DataValidationArtifact):
        self.feature_engineering_config = feature_engineering_config
        self.data_validation_artifact = data_validation_artifact
    
    def initiate_feature_engineering(self) -> FeatureEngineeringArtifact:
        """
        Initiates the feature engineering process.

        Parameters:
        self (FeatureEngineering): The instance of the FeatureEngineering class.
        Returns:
        FeatureEngineeringArtifact: An object containing the path to the transformed data.

        Raises:
        AppException: If an error occurs during the feature engineering process.

        """
        try:
            logging.info('Starting feature engineering')
            # Load validated data
            data_path = self.data_validation_artifact.vaildated_data_path
            transformed_data_path = os.path.join("artifacts", "transformed_data")

            if not os.path.exists(transformed_data_path):
                os.makedirs(transformed_data_path)

            # Example: Apply transformations (e.g., resize, normalize)
            for img_file in os.listdir(data_path):
                img = cv2.imread(os.path.join(data_path, img_file))
                # Apply transformations (example)
                img_resized = cv2.resize(img, (self.feature_engineering_config.feature_params['width'], self.feature_engineering_config.feature_params['height']))
                img_normalized = img_resized / 255.0  # Normalizing

                # Save the transformed image
                transformed_file_path = os.path.join(transformed_data_path, img_file)
                cv2.imwrite(transformed_file_path, img_normalized * 255)

            feature_engineering_artifact = FeatureEngineeringArtifact(transformed_data_path=transformed_data_path)
            logging.info(f"Feature engineering completed. Transformed data saved at {transformed_data_path}")

            return feature_engineering_artifact
        except Exception as e:
            raise AppException(e, sys)
