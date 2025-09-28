from fastapi import FastAPI, Depends, Response, HTTPException
from gpt import get_response

from auth import security, verify_password, create_access_token, config, hash_password
from sqlalchemy.orm import Session
from schemas import PromptSchema, RegisterLoginSchema
from database import User, Message, Chat, get_db
from authx import TokenPayload

import uvicorn





app = FastAPI()


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



#chat_history = [] # {'role' : '*assistant/user*', 'content' : prompt}
#@app.post('/chat', tags=['Main chat'])
#def chat(data: PromptSchema, payload: TokenPayload = Depends(security.access_token_required)):
    #chat_history.append({'role' : 'user', 'content' : data.prompt})
    #result = get_response(chat_history)           # теперь dict {'text','provider'}
    #chat_history.append({'role' : 'assistant', 'content' : result})
    #return {'result': result}



@app.post('/chats/{chat_name}/chat', tags=['Chat with AI'])
def chat(data: PromptSchema, username: str, chat_name: str = "New chat", payload: TokenPayload = Depends(security.access_token_required), db: Session = Depends(get_db))
    username = payload.sub
    db_user = db.query(User).filter(User.username==username).first()
    if not db_user:
        raise HTTPException(status_code=403, detail='Anauthorise!')
    db_chat = db.query(Chat).filter(Chat.user_id == db_user.id, Chat.title == chat_name).first()
    if not db_chat:
        db_chat = Chat(title=chat_name, user_id=db_user.id)
        db.add(db_chat)
        db.commit()
        db.refresh(db_chat)
    
    new_message = Message(sender=db_user, content=data, chat_id=db_chat.id)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    chat_history = [el for el in db.query(Message).filter(Message.chat_id == db_chat.id, User.username == db_user.username)]








if __name__ == '__main__':
    uvicorn.run('main:app', port=3000, host="0.0.0.0", reload=True)