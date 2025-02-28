from fastapi import APIRouter,HTTPException, status,Depends
from db.models.user import User
from db.client import db_client 
from db.schemas.user import user_schema
import jwt
from jose import JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone


app = APIRouter(prefix="/usersdb", tags=["usersdb"], 
                responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}) 
crypt = CryptContext(schemes=["bcrypt"])
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION_MINUTES = 1
SECRET_KEY = "5464832188i"  # Clave secreta para encriptar el token


user_list=[]	

@app.get("/usersclass/")

async def usersclass():
   #return User(name="John", age=25, email="john@notengo.com", url="https://www.casitengo.com")
    return user_list

#operacion para introducir un nuevo usuario en la Base de datos
@app.post("/",response_model=User,status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    
    user_dict = dict(user)
    if search_user_byUsername(user_dict.get("username")):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username already exists")
    else:   
        user_dict.pop("id")
        id=db_client.users.insert_one(user_dict).inserted_id
        new_user=user_schema(db_client.users.find_one({"_id":id}))
        return User(**new_user)

@app.get("/{user}",response_model=User,status_code=status.HTTP_200_OK)
async def get_users(user: str):
    user=search_user_byUsername(user)
    
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username not exists")
   # user=search_user_byUsername(user)
    return User(**user)


#API Modificar un usuario en la base de Datos------------------------------------
@app.put("/", response_model=User, status_code=status.HTTP_200_OK)
async def update_user(user_update: User):
    if not search_user_byUsername(str(user_update.username)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username not exists")
    else:
        user_dict = dict(user_update)
        user_dict.pop("id")
        db_client.users.find_one_and_update(
            {"username": user_update.username},
            {"$set": user_dict}
        )
        return user_update
   
    

    # API para eliminar un usuario------------------------------------
@app.delete("/{username}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str):
    if not search_user_byUsername(username):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username not exists")
    db_client.users.find_one_and_delete({"username":username})
     

  #Funcion para Buscar usuario por username-------------------------------------      
def search_user_byUsername(username: str):
    try:
        username_bd=db_client.users.find_one({"username":username})
        return user_schema(username_bd)
    except:
        return None
    
      
   
#para crear un usuario con contraseña encriptada------------------------------------
@app.post("/createuser",response_model=User,status_code=status.HTTP_201_CREATED)
async def create_user_with_pass(user: User):
    
    user_dict = dict(user)
    if search_user_byUsername(user_dict.get("username")):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username already exists")
    else:   
        user_dict.pop("id")
        password=user_dict.get("password")
        encrypted_password=encrypt_password(password)
        user_dict["password"]=encrypted_password
        id=db_client.users.insert_one(user_dict).inserted_id
        new_user=user_schema(db_client.users.find_one({"_id":id}))
        return User(**new_user)
    

    # funcion Login------------------------------------
    
@app.post("/login",response_model=str,status_code=status.HTTP_202_ACCEPTED)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        userI=await get_users(str(form_data.username))
    except:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Username not exists")
   
    if  jwt.decode(userI.password, SECRET_KEY, algorithms=[ALGORITHM]).get("password")==form_data.password: 
            return "Login successful"
    else:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")
    

# Función para encriptar la contraseña------------------------------------

def encrypt_password(password: str) -> str:
    payload = {
        "password": password,
        "exp": datetime.now(timezone.utc) + timedelta(days=1)  # Expira en 1 día
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) 