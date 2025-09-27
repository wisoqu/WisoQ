from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    username: str = Field(max_length=15)
    password: str = Field(min_length=8, max_length=20)
