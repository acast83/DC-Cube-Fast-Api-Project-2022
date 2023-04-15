"""
Logger setup module
"""
import logging

# Setting a logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("project.log")
log.addHandler(file_handler)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")

file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)
