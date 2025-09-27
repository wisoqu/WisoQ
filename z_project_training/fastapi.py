from fastapi import FastAPI, Depends
from schema import UserSchema
from DB import get_db
from models import UserModel
from sqlalchemy.orm import Session
import uvicorn


app = FastAPI()


@app.post('/regestreting')
def registation(user: UserSchema, db: Session = Depends(get_db)):
    new_user = UserModel(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    




if __name__ == '__main__':
    uvicorn.run('fastapi:app', reload=True)