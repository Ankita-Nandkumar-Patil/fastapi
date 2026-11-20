from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from models import Todo


from schemas import TodoCreate, TodoResponse, TodoUpdate, TodoReplace

app = FastAPI()


# ############ instead of separate api for each filter, we will include this logic in "get /todos" api only ##############
# @app.get("/todos/completed", response_model=list[TodoResponse])
# def get_completed_todos(
#     db: Session = Depends(get_db)
# ):
#     # statement = select(Todo).where(Todo.is_completed == True)

#     statement = select(Todo).where(Todo.iscompleted.is_(True))

#     result = db.execute(statement)

#     completed_todos = result.scalars().all()

#     return completed_todos

######################################

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.get(Todo, todo_id)

    if todo is None:
        raise HTTPException( status_code = 404, detail="record not found")
    
    return todo


@app.get("/todos", response_model= list[TodoResponse])
def get_todos(
        is_completed: bool | None = None,
        db: Session=Depends(get_db)
    ):

    statement = select(Todo)  #builds sql query statement: doesn't execute yet

    # Filtering by completed status
    if is_completed is not None:
        statement = select(Todo).where(Todo.is_completed.is_(is_completed))

    result = db.execute(statement)  #executes the statement

    todos = result.scalars().all() 
    # .scalars() = extracts the Todo objects from result rows
    #  .all() = collects all extracted objects into a python list
    return todos


@app.post("/todos", response_model=TodoResponse)
def create_todo(
    todo: TodoCreate,
    db : Session = Depends(get_db)
):
    todo_data = todo.model_dump() #converts pydantic model into dictionary
    new_todo = Todo(**todo_data)  #unpack the dictionary key-values
    
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

@app.patch("/todos/{todo_id}", response_model= TodoResponse)
def update_todo(
    todo_id : int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):

    existing_todo = db.get(Todo, todo_id)

    if existing_todo is None:
        raise HTTPException(status_code=404, detail="record not found")

    update_data = todo.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    for key, val in update_data.items():
        setattr(existing_todo, key, val)

    # db.add(existing_todo)  ==> db.get() aready makes it a persistent object associated with the Session.
    # so we don't need to do db.add() again

    # db.add() is primarily useful when you're introducing an object into the Session, like when creating a new Todo.

    db.commit()
    db.refresh(existing_todo)

    return existing_todo

@app.put("/todos/{todo_id}", response_model= TodoResponse)
def replace_todo(
    todo_id: int,
    todo: TodoReplace,
    db: Session = Depends(get_db)
):
    existing_todo = db.get(Todo, todo_id)

    if existing_todo is None:
        raise HTTPException(status_code=404, detail="record not found")

    update_data = todo.model_dump()

    for key, val in update_data.items():
        setattr(existing_todo, key, val) 

    #for PUT and PATCH : we never create a new Todo object. We modify the existing one, which is already tracked by SQLAlchemy. 

    db.commit()

    db.refresh(existing_todo)

    return existing_todo

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    existing_todo = db.get(Todo, todo_id)

    if existing_todo is None:
        raise HTTPException(status_code=404, detail="record not found")

    db.delete(existing_todo)

    db.commit()

    # No need for db.refresh() here. Once an object is deleted, refreshing it would be pointless because the row no longer exists.

    return {
        "detail": "todo record deleted successfully"
    }














