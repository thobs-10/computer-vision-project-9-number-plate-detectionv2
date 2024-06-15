from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    data_zip_file_path : str
    feature_store_path : str

@dataclass
class FeatureEngineeringArtifact:
    transformed_data_path: str

@dataclass
class DataValidationArtifact:
    validation_status: str
    data_status: bool
    vaildated_data_path: str

@dataclass
class ModelTrainerArtifact:
    trained_model_file_path : str
