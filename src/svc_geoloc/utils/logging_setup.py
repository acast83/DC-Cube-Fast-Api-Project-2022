"""
Logger setup module
"""
import logging
import os

# Setting a logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
current_file_folder = os.path.dirname(os.path.realpath(__file__))

file_handler = logging.FileHandler(f"{current_file_folder}/../../../logs/geoloc.log")
log.addHandler(file_handler)

formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")

file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)
