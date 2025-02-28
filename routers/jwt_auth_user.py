from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jose import JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION_MINUTES = 1
SECRET_KEY = "5464832188i"  # Clave secreta para encriptar el token

app = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="login")
crypt = CryptContext(schemes=["bcrypt"])


class User(BaseModel):  # usuario que viaja por la red
    username: str
    fullname: str
    email: str
    disable: bool


class UserInDB(User):  # usuario que esta en la base de datos que hereda del usuario original y tiene sus datos mas la contraseña
    password: str


user_db = {
    "ario": {
        "username": "ario",
        "fullname": "Ariel Castro",
        "email": "ariel871207@gmail.com",
        "disable": False,
        "password": "$2a$12$Sic75KS3hYN7fgOBgDp14eK2CHLUm3VJINzxMqS5LDknpstOK1G0y",
    },
    "dary": {
        "username": "dary",
        "fullname": "Darisleidi Acosta",
        "email": "daritacdj@gmail.com",
        "disable": False,
        "password": "$2a$12$Sic75KS3hYN7fgOBgDp14eK2CHLUm3VJINzxMqS5LDknpstOK1G0y",
    },
}


def search_user(username: str):  # funcion que busca un usuario NO en la base de datos
    if username in user_db:
        return UserInDB(**user_db[username])


async def auth_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = search_user(username)  # Buscar el usuario en la base de datos
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user  # Retornar el objeto UserInDB
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(user: UserInDB = Depends(auth_user)):
    if user.disable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    return user


@app.post("/login")  # ruta de autenticacion
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = user_db.get(form_data.username)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario no existe")

    user = search_user(form_data.username)

    if not crypt.verify(form_data.password, user.password):  # verifica la contraseña encriptada
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrecto")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION_MINUTES)
    access_token = {"sub": user.username, "exp": expire}
    return {
        "access_token": jwt.encode(access_token, SECRET_KEY, algorithm=ALGORITHM),
        "token_type": "bearer",
    }


@app.get("/users/me")  # ruta de acceso a los datos del usuario
async def me(user: User = Depends(get_current_user)):
    return user