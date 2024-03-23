from src.logger import logging
from src.exception import AppException
import sys
# logging.info('Starting')

try:
    a = 2/'s'
except Exception as e:
    raise AppException(e, sys)