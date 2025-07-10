from pymongo import MongoClient
from django.conf import settings

# Initialize MongoDB client and expose commonly used collections.
client = MongoClient(settings.MONGO_URI, connect=False)
db = client[settings.MONGO_DB_NAME]

# Collections in MongoDB correspond to tables in SQL.
questions_col = db['questions']
users_col = db['users']
user_activity_col = db['user_activity']


def get_next_user_id() -> str:
    """Generate a simple incremental user_id like U1, U2, ..."""
    last = users_col.find_one(sort=[('user_id', -1)])
    if last and 'user_id' in last:
        try:
            last_num = int(str(last['user_id'])[1:])
            return f"U{last_num + 1}"
        except (ValueError, TypeError):
            pass
    return 'U1'
