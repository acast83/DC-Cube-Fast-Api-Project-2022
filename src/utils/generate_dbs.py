from src.svc_users.utils.create_db import create_db as create_user_db
from src.svc_geoloc.utils.create_db import create_db as create_geoloc_db

if __name__ == '__main__':
    create_user_db()
    create_geoloc_db()
