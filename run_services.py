import subprocess
import time

for cmd in ("python src/svc_users/api/users.py", "python src/svc_geoloc/api/geoloc.py"):
    subprocess.Popen(cmd, shell=True)

while True:
    time.sleep(100)
