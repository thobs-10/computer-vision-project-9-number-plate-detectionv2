import os,sys
import yaml
from src.utils.main_utils import read_yaml_file
from src.logger import logging
from src.exception import AppException
from src.entity.config_entity import ModelTrainerConfig
from src.entity.artifacts_entity import ModelTrainerArtifact

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig = ModelTrainerConfig()):
        try:
            self.model_trainer_config = model_trainer_config
        except Exception as e:
            raise AppException(e, sys)
        
    def initiate_model_trainer(self)-> ModelTrainerArtifact:
        logging.info("Starting model Trainer")
        try:
            logging.info("unzipping data folder")
            os.system("unzipping data.zip")
            os.system("rm data.zip")
            logging.info("Extracting zip file")

            with open("data.yaml", "r") as f:
                num_classes = str(yaml.safe_load(f)['nc'])

            model_config_file_name = self.model_trainer_config.model_weight_name.split('.')[0]

            config_file = read_yaml_file(f"yolov8/models/{model_config_file_name}.yaml")

            config_file['num_classes'] = int(num_classes)

            with open(f"yolov8/models/custom_{model_config_file_name}.yaml", "w") as f:
                yaml.safe_dump(config_file, f, default_flow_style=False)

            os.system(f"python yolov8/train.py --img 416 --batch {self.model_trainer_config.batch_size} --epochs {self.model_trainer_config.no_epochs} --data yolov5/data/data.yaml --cfg yolov5/models/{model_config_file_name}.yaml --weights yolov5/weights/{self.model_trainer_config.model_weight_name} --cache yolov5/cache")

        except Exception as e:
            raise AppException(e, sys)
