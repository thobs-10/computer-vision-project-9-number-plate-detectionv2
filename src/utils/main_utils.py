import os.path
import sys
import yaml
import base64

from src.logger import logging
from src.exception import AppException


def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            logging.info('Reading yaml file sucessfully')
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise AppException(e, sys)

def write_yaml_file(file_path: str, data: object, replace: bool) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f'Deleting existing yaml file: {file_path}')
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "w") as yaml_file:
                logging.info('Writing yaml file sucessfully')
                yaml.dump(data, yaml_file, default_flow_style=False)
    except Exception as e:
        raise AppException(e, sys)
    
def decode_image(img_string, filename):
    imgdata = base64.b64decode(img_string)
    with open(filename, "wb") as fh:
        fh.write(imgdata)
        fh.close()

def encode_into_base64(cropped_image_path):
    with open(cropped_image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())
        return encoded_image.decode("utf-8")
    
