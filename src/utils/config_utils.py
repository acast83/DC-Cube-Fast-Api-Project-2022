import yaml
import pathlib
import os
from fastapi import HTTPException,status

current_file_folder = os.path.dirname(os.path.realpath(__file__))

def load_conf():
    # Open the YAML file and read its contents
    configuration_path = pathlib.Path(current_file_folder+"/../configuration/services.yaml").resolve()
    with open(configuration_path, "r") as f:
        data = f.read()

    # Parse the YAML data into a Python object
    config = yaml.safe_load(data)
    return config
    ...


def get_service_name(port):
    # Read the configuration from the YAML file
    configuration_path = pathlib.Path(current_file_folder+"/../config/services.yaml").resolve()


    with open(str(configuration_path), "r") as f:
        config = yaml.safe_load(f)

    # Loop through the services in the configuration
    for service_name, service_config in config["services"].items():
        # Check if the port number matches the service's port number
        if service_config["port"] == port:
            return service_name

    # If no matching service is found, return None
    raise HTTPException(status.HTTP_404_NOT_FOUND,detail="SERVICE_NOT_FOUND")
