import subprocess
import time

for cmd in ("python src/svc_users/api/users.py", "python src/svc_geoloc/api/geoloc.py"):
    subprocess.Popen(cmd, shell=True)

while True:
    time.sleep(100)
'''
sudo vim /etc/nginx/conf.d/my_microservices.conf

upstream users_service {
    server localhost:8001;
}

upstream geoloc_service {
    server localhost:8002;
}

server {
    listen 80;
    server_name localhost;

    location /api/users/ {
        rewrite ^/api/users(/.*)$ $1 break;
        proxy_pass http://users_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api/geoloc/ {
        rewrite ^/api/geoloc(/.*)$ $1 break;
        proxy_pass http://geoloc_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}


'''
