"""
Logger setup module
"""
import logging
# Setting a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("project.log")
logger.addHandler(file_handler)

formatter = logging.Formatter(
    "%(asctime)s:%(created)f:%(levelname)s:%(message)s")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
