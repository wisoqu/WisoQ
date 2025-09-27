from fastapi import FastAPI, Depends, Response, HTTPException
from gpt import get_response

from auth import security, verify_password, create_access_token, config, hash_password
from sqlalchemy.orm import Session
from schemas import PromptSchema, RegisterLoginSchema
from database import User, Message, Chat, get_db
from authx import TokenPayload

import uvicorn





app = FastAPI()
chat_history = [] # {'role' : '*assistant/user*', 'content' : prompt}

#Will i learn how to use GIT and GITHUB?
# Authorisation

@app.post('/register', tags=['Auth'], summary='register')
def register(user: RegisterLoginSchema, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail='User alreay exist!')
    #db_user.password = hash_password(user.password)
    db_user = User(username=user.username, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_access_token(str(db_user.username))
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'username' : db_user.username, 'msg' : 'Registrated successfilly!', 'token' : token}

#Используется username вместо id.

@app.post('/login', tags=['Auth'], summary='log in')
def login(user: RegisterLoginSchema, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail='User not found')
    is_right = verify_password(user.password, db_user.password)
    if not is_right:
        raise HTTPException(status_code=401, detail='Wrong password')
    token = create_access_token(str(db_user.username))
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'username' : db_user.username,'token' : token}




# Chat and other users logic

@app.get('/whatthehell')
def wth(payload: TokenPayload = Depends(security.access_token_required)):
    return payload.sub




@app.post('/chat', tags=['Main chat'])
def chat(data: PromptSchema, payload: TokenPayload = Depends(security.access_token_required)):
    chat_history.append({'role' : 'user', 'content' : data.prompt})
    result = get_response(chat_history)           # теперь dict {'text','provider'}
    chat_history.append({'role' : 'assistant', 'content' : result})
    return {'result': result}








if __name__ == '__main__':
    uvicorn.run('main:app', port=3000, host="0.0.0.0", reload=True)