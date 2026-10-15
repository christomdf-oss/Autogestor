from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import Base, engine

import models

from routes import vehiculos
from routes import usuarios


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoGestor API",
    description="Sistema de gestión de inventario automotriz",
    version="1.0.0"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


app.include_router(usuarios.router)
app.include_router(vehiculos.router)


@app.get("/", include_in_schema=False)
def interfaz_principal():

    return FileResponse(
        "templates/index.html"
    )