import requests, lxml.html
import time
import base64
import urllib3
from unidecode import unidecode
from bs4 import BeautifulSoup as bs
from fastapi import HTTPException

# temporary fix for SSL error
urllib3.disable_warnings()

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

    login = session.get(f"{base_url}{sigaa_initial_url}", verify=False)
    login_html = lxml.html.fromstring(login.text)

    login_hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

    login_form = {x.attrib["name"]: x.attrib["value"] for x in login_hidden_inputs}
    login_form["user.login"] = username
    login_form["user.senha"] = password

    response = session.post(f"{base_url}{url_to_login}", data=login_form)

    if "Ops!" in response.text or "Ocorreu um problema." in response.text:
        raise HTTPException(status_code=400, detail="Page problem")

    if "Usuário e/ou senha inválidos" in response.text:
        raise HTTPException(status_code=400, detail="Invalid credentials")

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


def grab_user_history(session, response):
    history_form = {}

    soup = bs(response.text, "html.parser")
    menu_div = soup.find("div", {"id": "menu-dropdown"})
    form = menu_div.find("form")

    user_id, action = grab_user_id(response)

    action[
        list(action.keys())[0]
    ] = "menu_form_menu_discente_j_id_jsp_1325243614_85_menu:A]#{ portalDiscenteUFPI.historico }"

    history_form[list(user_id.keys())[0]] = list(user_id.values())[0]
    history_form[list(action.keys())[0]] = list(action.values())[0]
    history_form[form["name"]] = form["id"]
    history_form["javax.faces.ViewState"] = "j_id1"
    url = form["action"]

    response = session.post(f"{base_url}{url}", data=history_form)

    encoded_bytes = base64.b64encode(response.content)

    payload = {
        "mime": "application/pdf",
        "image": encoded_bytes,
        "params": None,
    }

    return payload


def grab_user_registration_statement(session, response):
    statement_form = {}

    soup = bs(response.text, "html.parser")
    menu_div = soup.find("div", {"id": "menu-dropdown"})
    form = menu_div.find("form")

    user_id, action = grab_user_id(response)

    action[
        list(action.keys())[0]
    ] = "menu_form_menu_discente_j_id_jsp_1325243614_85_menu:A]#{ declaracaoVinculo.emitirDeclaracao }"

    statement_form[list(user_id.keys())[0]] = list(user_id.values())[0]
    statement_form[list(action.keys())[0]] = list(action.values())[0]
    statement_form[form["name"]] = form["id"]
    statement_form["javax.faces.ViewState"] = "j_id1"
    url = form["action"]

    response = session.post(f"{base_url}{url}", data=statement_form)

    encoded_bytes = base64.b64encode(response.content)

    payload = {
        "mime": "application/pdf",
        "image": encoded_bytes,
        "params": None,
    }

    return payload


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


def see_all_subjects(response):
    soup = bs(response.text, "html.parser")
    subjects = soup.find("div", {"id": "turmas-portal"})

    t_head = subjects.find("thead")
    item_title = [
        unidecode(title.text.replace(" ", "_").strip().lower())
        for title in t_head.find_all("th")
        if title.text != ""
    ]

    item_title[3] = "class_id"
    item_title.append("form_acessarTurmaVirtual")

    t_body = subjects.find("tbody")
    t_body_tr = t_body.find_all("tr")

    class_content = []

    for i, tr in enumerate(t_body_tr[:]):
        td = tr.find_all("td")

        if len(td) == 6:
            class_item = [data.text.replace("\n", "").strip() for data in td[:3]]
            class_item.append(td[0].find("input", {"name": "idTurma"})["value"])

            if i > 0:
                class_item.append(
                    td[0].find(
                        "input", {"name": f"form_acessarTurmaVirtualj_id_{int(i/2)}"}
                    )["value"]
                )

            else:
                class_item.append(
                    td[0].find("input", {"name": "form_acessarTurmaVirtual"})["value"]
                )

            class_content.append(class_item)

    return [dict(zip(item_title, item)) for item in class_content]
