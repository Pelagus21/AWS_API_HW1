from datetime import datetime, timezone
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = ""
# you can get API keys for free here 
MY_KEY = ""

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location, date):
    url_base_url = "https://weather.visualcrossing.com"
    url_api = "VisualCrossingWebServices/rest/services/timeline"
    unitGroup = "metric"

    url = f"{url_base_url}/{url_api}/{location}/{date}?unitGroup={unitGroup}&key={MY_KEY}"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        weather_info = json.loads(response.text)
        res = {
            "temperature_cels" : weather_info['days'][0]['temp'],
            "pressure_millibars": weather_info['days'][0]['pressure'],
            "visibility_km" : weather_info['days'][0]['visibility'],
            "windspeed_kmph" : weather_info['days'][0]['windspeed'],
            "humidity_perc" : weather_info['days'][0]['humidity'],
            "sunrise" : weather_info['days'][0]['sunrise'],
            "sunset" : weather_info['days'][0]['sunset'],
            "description" : weather_info['description']
        }
        return res
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>Homework 1: Weather fetcher</h2></p>"


@app.route("/content/api/v1/integration/weatherinfo", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    if json_data.get("location") is None:
        raise InvalidUsage("location is not provided", status_code=400)

    if json_data.get("date") is None:
        raise InvalidUsage("date for request is not provided", status_code=400)

    if json_data.get("user_name") is None:
        raise InvalidUsage("api user name is not provided", status_code=400)

    token = json_data.get("token")
    location = json_data.get("location")
    date = json_data.get("date")
    user_name = json_data.get("user_name")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    weather_info = get_weather(location, date)

    current_utc_datetime = datetime.now(timezone.utc)

    timestamp = current_utc_datetime.isoformat(timespec='seconds').replace('+00:00', 'Z')

    result = {
        "message": f"weather is fetched for {user_name}",
        "location": location,
        "date": date,
        "weather_info": weather_info
    }

    return result
