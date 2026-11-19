from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from schemas import TodoCreate, TodoFetch, TodoUpdate, TodoReplace

app = FastAPI()

@app.get("/todos")
def get_todos(db: Session=Depends(get_db)):
    result = db.execute(text("SELECT * FROM todos"))
    todos = [dict(row) for row in result.mappings().all()]

    return todos

@app.post("/todos")
def create_todo(
    todo: TodoCreate,
    db: Session = Depends(get_db)
):
    new_todo = todo.model_dump()
    try:
        result = db.execute(text("""
            INSERT INTO todos(title, description)
            VALUES(:title, :description)
            RETURNING id, title, description, is_completed
        """),
        new_todo)

        created_todo = result.mappings().one()

        db.commit()

        return dict(created_todo)
    except Exception:
        db.rollback()
        raise

@app.get("/todos/{todo_id}", response_model= TodoFetch)
def get_todo(
        todo_id: int, 
        db: Session = Depends(get_db)
    ):
        try:
            result = db.execute(text("SELECT * FROM todos WHERE id = :id"), {"id" : todo_id})

            fetched_todo = result.mappings().one_or_none()

            if fetched_todo is None:
                raise HTTPException(
                    status_code = 404,
                    detail = "record not found"
                )

            return dict(fetched_todo)
        except Exception:
            db.rollback()
            raise

@app.patch("/todos/{todo_id}")
def update_todo(
    todo_id: int,
    todo: TodoUpdate,
    db: Session = Depends(get_db)
):
    update_data = todo.model_dump(exclude_unset=True)

    allowed_fields = { "title", "description", "is_completed"}

    if not update_data:
        raise HTTPException(status_code=400, detail ="no fields provided")

    if not set(update_data).issubset(allowed_fields):
        raise HTTPException(status_code=400, detail="invalid fields")

    fields = [f"{key}= :{key}" for key in update_data.keys()]
    query = ", ".join(fields)

    params = { 
            **update_data,
            "id": todo_id
        }
    
    try:
        

        sql = f""" 
            UPDATE todos
            SET {query}
            WHERE id = :id
            RETURNING id, title, description, is_completed
        """

        
        result = db.execute(text(sql),params)

        updated_todo = result.mappings().one_or_none()

        if updated_todo is None:
            raise HTTPException(status_code=404, detail="record not found")

        db.commit()

        return dict(updated_todo)
    except Exception:
        db.rollback()
        raise


@app.put("/todos/{todo_id}")
def replace_todo(
    todo_id: int,
    todo: TodoReplace,
    db: Session = Depends(get_db)
):
    new_todo = todo.model_dump()

    try:

        # update_todo = db.execute(text("SELECT * FROM todos WHERE id =:id"), {"id": todo_id})

        # data = update_todo.mappings().one_or_none()

        

        replace_todo = db.execute(text(""" 
            UPDATE todos
            SET 
                title = :title,
                description = :description,
                is_completed = :is_completed
            WHERE id = :id
            RETURNING id, title, description, is_completed
        """), {
            "title" : new_todo["title"],
            "description" : new_todo["description"],
            "is_completed" : new_todo["is_completed"],
            "id" : todo_id
        })

        updated_todo = replace_todo.mappings().one_or_none()

        if updated_todo is None:
            raise HTTPException(status_code=404, detail="record not found")  

        db.commit()
        return dict(updated_todo)
    except Exception:
        db.rollback()
        raise

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db)
):
    try:
        # todo = db.execute(text("SELECT * FROM todos WHERE id = :id"), {"id": todo_id})

        # todo_data = todo.mappings().one_or_none()

        # if todo_data is None:
        #     raise HTTPException(status_code=404, detail="record not found")

        result = db.execute(text("""
            DELETE FROM todos WHERE id = :id
            RETURNING id, title
        """), {"id" : todo_id})

        data = result.mappings().one_or_none()

        if not data:
            raise HTTPException(status_code=404, detail="record not found")
        
        db.commit()
        return {"message": "Todod deleted successfully"}
    except Exception:
        db.rollback()
        raise
