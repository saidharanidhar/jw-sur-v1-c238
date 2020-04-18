import json
import os

import gspread
from flask import Flask
from flask_cors import CORS
from oauth2client.service_account import ServiceAccountCredentials

from helpers import RegexConverter

FILENAME = os.environ["FILENAME"]
GOOGLE_APPLICATION_CREDENTIALS = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_APPLICATION_CREDENTIALS)

CLIENT = gspread.authorize(CREDS)
app = Flask(__name__)

app.url_map.converters['regex'] = RegexConverter

CORS(app)

RETRY_SETTINGS = dict(tries=3, delay=1, backoff=2)