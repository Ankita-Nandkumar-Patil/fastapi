# import os
# from dotenv import load_dotenv


# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker, Session

# from fastapi import FastAPI, Depends

# load_dotenv()


# DATABASE_URL = os.getenv("DATABASE_URL")

# if not DATABASE_URL:
#     raise RuntimeError("Database url is not configured")
    

# engine = create_engine(DATABASE_URL)  #manages db connectivity

# with engine.connect() as connection:
#     result = connection.execute(text("SELECT 1"))
#     print(result.scalar())

# # with is a context manager. It ensures the connection is returned to the connection pool when the block finishes, even if an exception occurs.

# SessionLocal = sessionmaker(bind=engine)  #creates session objects

# #sessionlocal should be defined once at the module level, not recreated every time you need a Session.

# db = SessionLocal()   #db is an actual session

# # #########  Explicit Transaction Management ##############
# # try:
# #     db.execute(
# #         text(
# #             """
# #                 INSERT INTO todos(title, description)
# #                 VALUES (:title, :description)
# #             """
# #         ),
# #         {
# #             "title" : "Learn DB transactions again",
# #             "description" : "understand commit and rollback"
# #         }
# #     )

# #     # :title, :description => bound parameters = sqlalchemy safely passes their values to the db instead of constructing sql by concatinating strings

# #     db.commit()
# # except Exception:
# #     db.rollback()
# #     raise
# # finally:
# #     db.close()




# # #########  Transaction context manager ##############
# try:
#     with db.begin():
#         db.execute(
#             text("""
#                 INSERT INTO todos(title, description) VALUES(:title, :description)
#             """),
#             {"title": "learn context manager", "description" : "implement insertion"}
#         )

# finally: 
#     db.close()

# app = FastAPI()

# def get_db():
#     db = SessionLocal() #Creates a new SQLAlchemy Session.
#     try:
#         yield db #temporarily pauses the function and provides the Session to FastAPI.
#         # FastAPI then passes that Session to the endpoint.
#     finally: db.close()   #FastAPI resumes the dependency and executes the finally block.

# @app.get("/todos")
# async def get_todos(db: Session = Depends(get_db)):
