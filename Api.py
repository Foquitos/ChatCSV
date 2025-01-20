import uvicorn
import pandas as pd

from ChatCSV import ChatCSV
from typing import Optional
from sqlalchemy import text
from pydantic import BaseModel
from jose import JWTError, jwt
from sqlalchemy import create_engine
from Variables import connection_string, SECRET_KEY
from datetime import datetime, timedelta, timezone  
from fastapi import FastAPI, HTTPException, Form, Depends, status

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

class User(BaseModel):
    usuario: int
    Nombre: Optional[str] = None
    legajo: Optional[str] = None
    password: Optional[str] = None    
engine = create_engine(connection_string)
# Configuración de seguridad
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelo de usuario


# Configuración de password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


df_usuarios = pd.read_sql("""SELECT
        n.documento usuario
        ,[password]
        ,n.nombre + ' ' + n.apellido Nombre
        ,n.legajo
    FROM [Mera].[dbo].[passwords] p
    right join nomina n on n.id = p.nomina_id
    join operadores o on n.id = o.legajo_id and o.fecha_hasta is null and o.estado = 1""", engine)

app = FastAPI()
chat_csv = ChatCSV()
# chat_csv.Armar_embedding('documentacion depurada')  # Prepara el embedding (esto puede ser costoso si no tienes un índice ya creado)
chat_csv.Usar_embedding_armado()
chat_csv.Prompts()
chat_csv.Armar_Query()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(documento:int):
    df = pd.read_sql(f"""SELECT
        n.documento usuario
        ,[password]
        ,n.nombre + ' ' + n.apellido Nombre
        ,n.legajo
    FROM [Mera].[dbo].[passwords] p
    right join nomina n on n.id = p.nomina_id
    join operadores o on n.id = o.legajo_id and o.fecha_hasta is null and o.estado = 1
    where documento = {str(documento)}""", engine)
    
    if df.empty == False:
        usuario = df.to_dict(orient='records')[0]
        return User(**usuario)
    else:
        return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user.password:
        raise HTTPException(status_code=404, detail="Usuario no tiene contraseña, Favor colocar la misma")
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: int = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
    
    user = get_user(int(username))
    if user is None:
        raise credentials_exception
    return user

@app.post("/change_password/")
async def change_password(
    documento: int = Form(...),
    password: str = Form(...),
    new_password: str = Form(...)
):
    """Endpoint para cambiar la contraseña de un usuario o generar la misma.

    Args:
        documento (int, optional): Documento del operador al cual se le desea cambiar la contraseña. Defaults to Form(...).
        password (str, optional): Contraseña actual. Defaults to Form(...).
        new_password (str, optional): Contraseña a cambiar. Defaults to Form(...).

    Raises:
        HTTPException status_code=500: Error interno
        HTTPException status_code=404: Usuario no encontrado
        HTTPException status_code=401: contraseña incorrecta

    Returns:
        _type_: _description_
    """    
    try:
        user = get_user(documento)
        if user.password == None:
            with engine.connect() as connection:
                query = text("""
                    INSERT INTO [Mera].[dbo].[passwords]
                    ([nomina_id]
                    ,[password])
                    VALUES
                    ((SELECT id FROM nomina WHERE documento = :documento)
                    ,:hashed_password)
                """)
                connection.execute(
                    query,
                    {
                        "documento": documento,
                        "hashed_password": pwd_context.hash(new_password)
                    }
                )
                connection.commit()
            return {"message": "Contraseña generada con éxito"}
        else:
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            if not verify_password(password, user.password):
                raise HTTPException(status_code=401, detail="Contraseña incorrecta")
            user.password = pwd_context.hash(new_password)
            with engine.connect() as connection:
                
                query = text("""
                    UPDATE [Mera].[dbo].[passwords]
                    SET [password] = :hashed_password
                    WHERE nomina_id = (SELECT id FROM nomina WHERE documento = :documento)
                """)
                connection.execute(
                    query,
                    {
                        "hashed_password": user.password,
                        "documento": documento
                    }
                )
                connection.commit()
            return {"message": "Contraseña cambiada con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/token/")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Genera un token de acceso para un usuario autenticado.
    La autenticación se realiza a través de JSON Web Token: https://jwt.io/introduction/. Una primer llamada de autenticación de credenciales devolverá un Token, que por la duración de la sesión podrá ser utilizado para consumir la información de la API, dicha token estara activo durante 30 minutos.
    Una vez obtenido el Token, basta incluirlo en llamadas posteriores en la cabecera Authorization (Authorization header), utilizando el schema Bearer.
    Authorization: Bearer <token>


    Args:
        form_data (OAuth2PasswordRequestForm, optional): Recibe en form data, username y password para recibir un bearer token de autenticacion . Defaults to Depends().

    Raises:
        HTTPException HTTP_400_BAD_REQUEST: El usuario debe ser una documento
        HTTPException HTTP_401_UNAUTHORIZED: Usuario o contraseña incorrectos

    Returns:
        _type_: Retorna un diccionario con el token de acceso y el tipo de token
    """
    try:
        username = int(form_data.username)
        user = authenticate_user(username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.usuario)},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be a number"
        )

@app.post("/consultar/")
async def consultar(
    query: str = Form(...),
    campana: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para realizar consultas a través del ChatCSV usando form-data.
    Requiere autenticación.
    """
    
    campana = campana.lower()
    if campana == 'csv':
        try:
                response = chat_csv.Realizar_consulta(query)
                return {"response": response, "user": current_user.usuario}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
            raise HTTPException(status_code=500, detail='Campaña no valida')

@app.post("/consultar_contexto/")
async def consultar_contexto(
    query: str = Form(...),
    campana: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para realizar consultas a través del ChatCSV usando form-data.
    Requiere autenticación.
    """
    
    campana = campana.lower()
    if campana == 'csv':
        try:
            response = chat_csv.Realizar_consulta_con_contexto(query)
            return {"response": response['response'],'context':response['context'], "user": current_user.usuario}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=500, detail='Campaña no valida')


@app.post("/refresh_embedding/")
async def consultar_contexto(
    campana: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    lista_refresh = chat_csv.refresh_embedding(campana)
    return {'quantity':len(lista_refresh),'campana':campana, "user": current_user.usuario, 'status':'Completed'}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)