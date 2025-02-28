from fastapi import APIRouter
from pydantic import BaseModel


app = APIRouter() 

class User(BaseModel):
    id: int
    name: str
    age: int
    email: str
    url: str

user_list=[User(id=1,name="John", age=25, email="john@casitengo.com", url="https://www.casitengo.com"),User(id=2,name="Ario", age=37, email="as@notengo.com", url="https://www.casitengo.com")]	

@app.get("/usersclass/")

async def usersclass():
   #return User(name="John", age=25, email="john@notengo.com", url="https://www.casitengo.com")
    return user_list

#operacion para introducir un nuevo usuario en la lista
@app.post("/createuser/")
async def create_user(user: User):
    if type(onlyuser(user.id))==User:
         return {"message":"User already exists"}
    else:
         user_list.append(user)
 


@app.get("/onlyuser/{id}")#query

async def onlyuser(id: int):
    user= filter (lambda user: user.id == id, user_list)
   #return User(name="John", age=25, email="john@notengo.com", url="https://www.casitengo.com")
    try:
        return list(user)[0]
    except:
        return {"message":"User not found"}
    
#create_user(User(id=1,name="Ario", age=37, email="arie@asd.com", url="https://www.casitengo.com"))
    