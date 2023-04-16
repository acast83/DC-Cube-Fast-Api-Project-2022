import subprocess
import time
import os

for cmd in ("python src/svc_users/api/users.py", "python src/svc_geoloc/api/geoloc.py"):
    subprocess.Popen(cmd, shell=True)
os.system("sudo systemctl restart nginx")

while True:
    time.sleep(100)
