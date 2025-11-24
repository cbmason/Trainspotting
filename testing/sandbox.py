import requests

BASE_URL = "https://api.pugetsound.onebusaway.org/api/where"
ROUTE_1_LINE_ID = "40_100479"
API_KEY = "ad0b7f8d-bde6-469a-a839-f5c7429fd665"
endpoint = "https://api.pugetsound.onebusaway.org/api/where/trips-for-route/40_100479.json"

def query_server():
    response = requests.get(endpoint, params={'key': API_KEY, 'includeStatus': 'true'})
    return response.json()