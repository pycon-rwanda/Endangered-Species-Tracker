import requests
from decouple import config


API_KEY = config("IUCN_API_KEY")


def fetch_data(endpoint, params=None):
    if params is None:
        params = {}
    try:
        response = requests.get(endpoint, params=params, 
                                headers={"Bearer": API_KEY}, timeout=None)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
