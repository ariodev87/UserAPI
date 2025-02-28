
from fastapi import FastAPI
from routers import user2
from routers import users_db
from routers import jwt_auth_user

app = FastAPI()
app.include_router(user2.app)
app.include_router(jwt_auth_user.app)
app.include_router(users_db.app)

@app.get("/testapi")
async def root():
    return "Hello World"



