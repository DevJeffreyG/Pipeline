from fastapi import FastAPI
import uvicorn

app = FastAPI(title="mi-microservicio")

@app.get("/health")
def health() -> dict:
    """Endpoint usado por el HEALTHCHECK de Docker y por el orquestador."""
    return {"status": "ok"}

@app.get("/saludo/{nombre}")
def saludo(nombre: str) -> dict:
    return {"mensaje": f"Hola, {nombre}!"}

""" if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) """
