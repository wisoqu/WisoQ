from fastapi import FastAPI, Response, dependencies, Depends
from authx import AuthX, AuthXConfig
from pydantic import BaseModel
from fastapi import HTTPException

# Написан пример реализации логина и доступа к защищенному эндпоинту

app = FastAPI()
config = AuthXConfig()
config.JWT_SECRET_KEY = 'SECRET_KEY'
config.JWT_ACCESS_COOKIE_NAME = 'my_access_token'
config.JWT_TOKEN_LOCATION = ["cookies"]
security = AuthX(config=config)
class UserLoginSchema(BaseModel):
    username: str
    password: str

@app.post('/login')
def login(creds: UserLoginSchema, response: Response):
    if creds.username == 'test' and creds.password == 'test':
        token = security.create_access_token(uid='12345')
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {'access_token' : token}
    raise HTTPException(status_code=401, detail={'error' : 'Bad creditans!'})


@app.get('/protected', dependencies=[Depends(security.access_token_required)])
def protected():
    return {'msg' : 'TOP SECRET DATA!'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('training:app', reload=True)