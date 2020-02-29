from fastapi import FastAPI, File

app = FastAPI()

from api import routes
