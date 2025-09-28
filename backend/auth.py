from authx import AuthX, AuthXConfig
from datetime import timedelta
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()



pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# my password, hashed
def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)
# Hashing data
def hash_password(password):
    return str(pwd_context.hash(password))
def create_access_token(username: str):
    return security.create_access_token(uid=username)

#Main settings
config = AuthXConfig()
config.JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
config.JWT_ACCESS_COOKIE_NAME = os.getenv('JWT_ACCESS_COOKIE_NAME', 'my_access_cookie')
config.JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '1')))
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)




#@app.get('/protected') EXAMPLE
#def protected_route(response: Response, payload: TokenPayload = Depends(security.access_token_required)):
#    return {'data' : 'successfully!', 'id' : payload.sub}
