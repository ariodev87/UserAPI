from fastapi import FastAPI,Depends,HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  #importar la clase de seguridad , modulo de autenticacion FASTAPI 

app = FastAPI() 
oauth2 = OAuth2PasswordBearer(tokenUrl="login") #instancia de la clase de seguridad



class User(BaseModel): #usuario que viaja por la red
    username: str  
    fullname: str
    email: str
    disable: bool

class UserInDB(User): #usuario que esta en la base de datos que hereda del usuario original y tiene sus datos mas la contraseña
    password: str

user_db={
    "ario":{
         "username": "ario"  ,
         "fullname": "Ariel Castro",
         "email": "ariel871207@gmail.com",
         "disable": False,
         "password": "123456"
    },"dary":{
         "username": "dary"  ,
         "fullname": "Darisleidi Acosta",
         "email": "daritacdj@gmail.com",
         "disable": False,
         "password": "123456"
    }

} 
def search_user(username: str): #funcion que busca un usuario NO en la base de datos
    if username in user_db:
        return User(**user_db[username])
    

def search_userdb(username: str): #funcion que busca un usuario en la base de datos
    if username in user_db:
        return UserInDB(**user_db[username])
    

async def get_current_user(token:str=Depends(oauth2)):#funcion que recibe el token y devuelve el usuario *(dependencia)*
    user=search_user(token)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                            detail="Credenciales de autenticacion invalidas",
                            headers={"WWW-Authenticate":"Bearer"})
    if user.disable:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="Usuario inactivo")
    return user




@app.post("/login") #ruta de autenticacion
async def login(form_data: OAuth2PasswordRequestForm = Depends()): #funcion de autenticacion
    user_data=user_db.get(form_data.username)
    if not user_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,detail="Usuario no existe")
    
    user=search_user(form_data.username)
    if not form_data.password==user.password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail="Password incorrecto")
    return {"access_token":user.username,"token_type":"bearer"}	#retorna el token de acceso

@app.get("/users/me") #ruta de acceso a los datos del usuario
async def me(user:User=Depends(get_current_user)):
    return user