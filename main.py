import scraping
import base_models
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index():
    return {"status": 200}


@app.post("/info")
async def return_info(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.grab_user_data(session, response)

    return info


@app.post("/notas")
async def see_grades(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.see_all_grades(session, response)

    return info

