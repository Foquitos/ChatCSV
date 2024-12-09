from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
import uvicorn

# Importar la clase ChatCSV
from ChatCSV import ChatCSV  # Ajusta 'your_chatcsv_module' al nombre de tu archivo Python.

# Crear la aplicación FastAPI
app = FastAPI()

# Instanciar la clase ChatCSV
chat_csv = ChatCSV()

# Inicializar los métodos necesarios
# chat_csv.Armar_embedding()  # Prepara el embedding (esto puede ser costoso si no tienes un índice ya creado)
chat_csv.Usar_embedding_armado()
chat_csv.Prompts()          # Configura los prompts
chat_csv.Armar_Query()      # Configura el motor de consulta

@app.post("/consultar/")
def consultar(query: str = Form(...)):
    """
    Endpoint para realizar consultas a través del ChatCSV usando form-data.
    """
    try:
        response = chat_csv.Realizar_consulta(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejecutar el servidor (solo si se ejecuta este archivo directamente)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)