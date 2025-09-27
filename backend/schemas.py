from pydantic import BaseModel, Field


class PromptSchema(BaseModel):
    prompt: str = Field(min_length=1)

class RegisterLoginSchema(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=20)
