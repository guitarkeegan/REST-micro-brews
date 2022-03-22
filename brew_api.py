import requests

ENDPOINT = "https://api.openbrewerydb.org/breweries"
BY_DISTANCE = "https://api.openbrewerydb.org/breweries?by_dist=38.8977,77.0365"


class BrewApi:
    def __init__(self, city_name):
        self.user_city = city_name.replace(" ", "_").lower()
        print(self.user_city)
        self.brew_requests = {
            "by_city": self.user_city,
            "by_type": "micro",
            "per_page": 9
        }


    def search_city(self):
        response = requests.get(ENDPOINT, params=self.brew_requests)
        response.raise_for_status()
        data = response.json()
        return data

    def search_id(self):
        pass

