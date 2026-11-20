from pydantic import BaseModel, Field, ConfigDict

class TodoCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None

class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int 
    title: str
    description: str | None
    is_completed: bool

class TodoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None

class TodoReplace(BaseModel):
    title: str
    description: str | None
    is_completed: bool