import requests
from retry import retry

from constants import HTTP_METHODS
from helpers import get_row_from_data, get_request_ip
from lookup import movie_list
from recommender.get_similar_movies import get_similar_movies
from settings import CLIENT, app, RETRY_SETTINGS, FILENAME
from utils import get_movie_posters


@app.route('/', methods=["GET"])
def health_check():
    from flask import request
    return get_request_ip(request)


@app.route('/<regex(".*"):url>/end/', methods=HTTP_METHODS)
def proxy(url):
    from flask import request
    method = request.method
    if method == "OPTIONS":
        return "ok"
    payload = request.data.decode("utf-8")
    response = requests.request(method=method, url=url, data=payload)
    if not response.ok:
        print(f"Error Occurred {response.content} {response.status_code}")
        return "Error", 500
    return response.text


@app.route('/fetch/', methods=["GET"])
def get_movies():
    from flask import request
    seq = 0
    page = 1
    page_size = 10
    try:
        seq = int(request.args.get("seq", "0"))
        page = int(request.args.get("page", "1"))
        page_size = int(request.args.get("page_size", "1"))
    except:
        pass

    required_indexes = [i * 2 + seq for i in range((page - 1) * page_size, page * page_size)]

    title_list = []
    if required_indexes[-1] < len(movie_list):
        title_list = [movie_list[index] for index in required_indexes]

    return dict(titles=get_movie_posters(title_list))


@app.route('/recommendations/', methods=["POST"])
def get_recommendations():
    from flask import request
    selection = request.json.get("selection", [])
    titles_required = int(request.json.get("titles_required", 20))
    title_list = get_similar_movies(selection, titles_required)
    return dict(titles=get_movie_posters(title_list))


@app.route('/submit/', methods=['POST'])
def submit():
    from flask import request
    data = request.get_json()

    ip = get_request_ip(request)
    sheet_id = int(data.get("sheet_id", 0))
    file_name = data.get("file_name", FILENAME)
    row = get_row_from_data(ip, data["data"])

    try:
        to_google_sheet(file_name, sheet_id, row)
    except Exception as e:
        print(f"Error Occurred {e}")

    return "ok"


@retry(**RETRY_SETTINGS)
def to_google_sheet(file_name, sheet_id, row):
    file = CLIENT.open(file_name)
    sheet = file.get_worksheet(sheet_id)
    sheet.append_row(row)


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
