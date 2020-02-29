from api import app, scraping, base_models
from starlette.responses import RedirectResponse


@app.get("/")
def index():
    return RedirectResponse(url="/docs")


@app.post("/info")
def return_info(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.grab_user_data(session, response)

    return info


@app.post("/ver-notas")
def return_grades(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.see_all_grades(session, response)

    return info


@app.post("/disciplinas")
def return_subjects(user: base_models.User):
    _, response = scraping.login(user.username, user.password)
    info = scraping.see_all_subjects(response)

    return info


@app.post("/historico")
def return_history(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    payload = scraping.grab_user_history(session, response)

    return payload


@app.post("/declaracao")
def return_registration_statement(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    payload = scraping.grab_user_registration_statement(session, response)

    return payload
