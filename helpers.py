import json
from datetime import datetime, timezone

import requests
from werkzeug.routing import BaseConverter

from constants import MAX_CELL_SIZE
from serializers import GeoLite

IP_SERIALIZER = GeoLite()


def get_request_ip(request):
    if not request.headers.getlist("X-Forwarded-For"):
        ip = request.remote_addr
    else:
        ip = request.headers.getlist("X-Forwarded-For")[0]
    return ip


def json_dump(data):
    return json.dumps(data, separators=(',', ':'))


def payload_chunks(payload, row):
    payload_dump = json_dump(payload)
    payload_split = [payload_dump[i:i + MAX_CELL_SIZE] for i in range(0, len(payload_dump), MAX_CELL_SIZE)]
    row.extend([len(payload_split), *payload_split])


def location(payload, row):
    ip_data = dict()
    ip = payload["ip"]
    try:
        response = requests.get("http://www.geoplugin.net/json.gp", params=dict(ip=ip), timeout=10)
        if response.ok:
            ip_data = IP_SERIALIZER.load(response.json())
        else:
            print(f"Error Occurred while requesting IP {response.content} {response.status_code}")
    except Exception as e:
        print(f"Error Occurred while loading IP {e}")
    row.append(json_dump(ip_data))


def feedback(payload, row):
    row.append(json_dump(payload.get("feedbackData", {}).get("feedback", {})))


def choice_titles_count(payload, row):
    titles = payload.get("choiceData", {}).get("titles", [])
    count = sum([len(title_row_data.get("items", [])) for title_row_data in titles])
    row.append(count)


def survey_titles_count(payload, row):
    row.append(len(payload.get("surveyData", {}).get("titles", [])))


def choice_time(payload, row):
    row.append(payload.get("choiceData", {}).get("duration"))


def survey_time(payload, row):
    row.append(payload.get("surveyData", {}).get("duration"))


def max_iteration(payload, row):
    row.append(payload.get("maxIterations"))


def iteration(payload, row):
    row.append(payload.get("iteration"))


def session_id(payload, row):
    row.append(payload.get("sessionID"))


def region(payload, row):
    row.append(payload.get("region"))


def timestamp(payload, row):
    ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    row.append(ts)


def identifier(payload, row):
    row.append(payload.get("identifier"))


function_sequence = [
    identifier,
    timestamp,
    region,
    session_id,
    iteration,
    max_iteration,
    survey_time,
    choice_time,
    survey_titles_count,
    choice_titles_count,
    feedback,
    location,
    payload_chunks
]


def get_row_from_data(ip, data):
    row = []
    data["ip"] = ip
    for func in function_sequence:
        func(data, row)
    return row


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]
