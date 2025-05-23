import bcrypt
import jwt
import datetime
from utils.database import query_db

SECRET_KEY = "your_secret_key_here"

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def register_user(email, password, name):
    hashed = hash_password(password)
    query = "INSERT INTO athlete_users (email, password_hash, name, created_at) VALUES (%s, %s, %s, NOW())"
    query_db(query, (email, hashed, name))

def authenticate_user(email, password):
    query = "SELECT id, password_hash FROM athlete_users WHERE email = %s"
    result = query_db(query, (email,))
    if result:
        user = result[0]
        if check_password(password, user['password_hash'].tobytes()):
            return user['id']
    return None
