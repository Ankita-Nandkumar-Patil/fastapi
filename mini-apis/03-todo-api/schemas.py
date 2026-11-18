from pydantic import BaseModel, Field

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None =  None

class TodoFetch(BaseModel):
    id: int
    title: str
    description: str | None
    is_completed: bool 

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None


class TodoReplace(BaseModel):
    title: str = Field(min_length =1 , max_length=255)
    description: str | None
    is_completed: bool 