"""
Logger setup module
"""
import logging
import os
import pathlib

from utils.config_utils import get_service_name

def get_logger(request):
    service_name = get_service_name(request.base_url.port)
    # Setting a logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)
    current_file_folder = os.path.dirname(os.path.realpath(__file__))
    log_file_path = pathlib.Path(f"{current_file_folder}/../../logs/{service_name}.log").resolve()
    file_handler = logging.FileHandler(str(log_file_path))
    log.addHandler(file_handler)

    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S")

    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)
    return log
