import requests

from retry import retry

from constants import HTTP_METHODS
from helpers import get_row_from_data
from settings import CLIENT, app, RETRY_SETTINGS, FILENAME


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


@app.route('/final/', methods=['POST'])
def save():
    from flask import request
    data = request.get_json()

    file_name = data.get("file_name", FILENAME)
    sheet_id = int(data.get("sheet_id", 0))
    row = get_row_from_data(request.remote_addr, data["data"])

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
