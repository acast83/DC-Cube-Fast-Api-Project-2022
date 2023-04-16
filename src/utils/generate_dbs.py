from svc_users.utils.db_utils import create_db as create_user_db
from svc_geoloc.utils.db_utils import create_db as create_geoloc_db

if __name__ == '__main__':
    create_user_db()
    create_geoloc_db()
