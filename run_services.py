import subprocess
import time
import os
from dotenv import load_dotenv
load_dotenv()
root_password=os.getenv("ROOT_PASS")
from utils.config_utils import load_conf

def start_services():
    config = load_conf()
    for service_name in config["services"]:
        subprocess.Popen(f"python src/svc_{service_name}/api/{service_name}.py", shell=True)

    print("stopping nginx")
    os.system(f"echo {root_password} | sudo -S systemctl stop nginx")
    print("\nstarting nginx")
    os.system(f"echo {root_password} | sudo -S systemctl start nginx")

    while True:
        time.sleep(100)

if __name__=="__main__":
    start_services()