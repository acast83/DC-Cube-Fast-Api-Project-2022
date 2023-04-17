import subprocess
import time
import os
from dotenv import load_dotenv
load_dotenv()
root_password=os.getenv("ROOT_PASS")

for cmd in ("python src/svc_users/api/users.py", "python src/svc_geoloc/api/geoloc.py"):
    subprocess.Popen(cmd, shell=True)

print("stopping nginx")
os.system(f"echo {root_password} | sudo -S systemctl stop nginx")
print("\nstarting nginx")
os.system(f"echo {root_password} | sudo -S systemctl start nginx")

while True:
    time.sleep(100)
