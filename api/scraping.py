import requests, lxml.html
import time
from unidecode import unidecode
from bs4 import BeautifulSoup as bs

base_url = "https://sigaa.ufpi.br"
sigaa_initial_url = "/sigaa/verTelaLogin.do"

url_to_login = "/sigaa/logar.do?dispatch=logOn"
url_after_login = "/sigaa/ufpi/portais/discente/discente.jsf"


def grab_user_id(response):
    user_id = {}
    action = {}

    form_hidden = lxml.html.fromstring(response.text)
    form_inputs = form_hidden.xpath(r'//form//input[@type="hidden"]')

    for inputs in form_inputs:
        if inputs.name == "id":
            user_id = {inputs.name: inputs.value}
        if inputs.name == "jscook_action":
            action = {inputs.name: inputs.value}

    return user_id, action


def login(username, password, matricula=None):
    session = requests.session()

    login = session.get(f"{base_url}{sigaa_initial_url}")
    login_html = lxml.html.fromstring(login.text)

    login_hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

    login_form = {x.attrib["name"]: x.attrib["value"] for x in login_hidden_inputs}
    login_form["user.login"] = username
    login_form["user.senha"] = password

    response = session.post(f"{base_url}{url_to_login}", data=login_form)

    return session, response


def grab_user_data(session, response):
    arr = []
    filtered = {}

    soup = bs(response.text, "html.parser")
    student_info = soup.find_all("div", {"id": "agenda-docente"})

    for item in student_info:
        item = item.text.replace("\t", "")
        item = item.replace(":", "")

        arr = item.split("\n")
        arr = [i for i in arr if i]

    # Filter matricula, curso, IRA
    for i, item in enumerate(arr):
        if (
            "Matrícula" in item
            or "Curso" in item
            or "IRA" in item
            or "Turno" in item
            or "Entrada" in item
        ):
            filtered[unidecode(arr[i].strip().lower())] = unidecode(arr[i + 1].strip())

    # Filter name
    name_info = soup.find("p", {"class": "info-docente"})
    name_info = name_info.text.replace("\n", "")

    filtered["nome"] = name_info.strip()
    filtered["imagem"] = grab_user_image(session, soup)
    filtered["semestre"] = grab_user_semester(soup)

    return filtered


def grab_user_image(session, soup):
    img = soup.find("div", {"class": "foto"}).find("img")
    # _img = session.get(f"{base_url}{img['src']}") # Image object content

    return f"{base_url}{img['src']}"


def grab_user_semester(soup):
    user_info = soup.find("div", {"id": "info-usuario"})
    semester = user_info.find("strong").text

    return semester


def post_to_grade_page(session, response):
    grades_post_form = {}

    soup = bs(response.text, "html.parser")
    menu_div = soup.find("div", {"id": "menu-dropdown"})
    form = menu_div.find("form")

    user_id, action = grab_user_id(response)

    action[
        list(action.keys())[0]
    ] = "menu_form_menu_discente_j_id_jsp_1325243614_85_menu:A]#{ relatorioNotasAluno.gerarRelatorio }"

    grades_post_form[list(user_id.keys())[0]] = list(user_id.values())[0]
    grades_post_form[list(action.keys())[0]] = list(action.values())[0]
    grades_post_form[form["name"]] = form["id"]
    grades_post_form["javax.faces.ViewState"] = "j_id1"
    url = form["action"]

    response = session.post(f"{base_url}{url}", data=grades_post_form)

    return response


def see_all_grades(session, response):
    arr = []

    response = post_to_grade_page(session, response)

    soup_notas = bs(response.text, "html.parser")
    emission_date = soup_notas.find("span", {"class": "dataAtual"})
    grades_table = soup_notas.find_all("table")

    emission_date = emission_date.text.strip()

    # Studend ID
    # for i, tables in enumerate(grades_table[1:2]):
    #     th = tables.find_all("th")
    #     td = tables.find_all("td")

    # Grades
    for i, tables in enumerate(grades_table[2:-1]):
        aux = {}

        period = tables.find("caption").text.strip()
        aux["periodo"] = period

        titles = tables.find_all("th")
        content = tables.find_all("td")
        aux["disciplinas"] = []

        # Parse text titles
        titles = [unidecode(item.text.strip()) for item in titles]
        titles = [item.replace(". ", "_") for item in titles]
        titles = [item.replace(" ", "_") for item in titles]
        titles = [item.lower() for item in titles]

        # Parse text content
        content = [unidecode(item.text.strip()) for item in content]
        content = [None if item == "" else item for item in content]
        content = [content[i : i + 11] for i in range(0, len(content), 11)]

        for data in content:
            aux["disciplinas"].append(dict(zip(titles, data)))

        arr.append(aux)

    return arr


def see_all_subjects(soup):
    pass
