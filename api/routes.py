from api import app, scraping, base_models


@app.get("/")
async def index():
    return {"status": 200}


@app.post("/info")
async def return_info(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.grab_user_data(session, response)

    return info


@app.post("/grades")
async def return_grades(user: base_models.User):
    session, response = scraping.login(user.username, user.password)
    info = scraping.see_all_grades(session, response)

    return info


@app.post("/subjects")
async def return_subjects(user: base_models.User):
    _, response = scraping.login(user.username, user.password)
    info = scraping.see_all_subjects(response)

    return info
