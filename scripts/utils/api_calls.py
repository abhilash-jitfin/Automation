import requests


class SimpleRequests:

    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'Token {token}'

    def get_url(self, endpoint):
        return self.base_url + endpoint

    def get(self, endpoint, **kwargs):
        response = requests.get(self.get_url(endpoint), headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data=None, **kwargs):
        response = requests.post(self.get_url(endpoint), data=data, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def patch(self, endpoint, data=None, **kwargs):
        response = requests.patch(self.get_url(endpoint), data=data, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint, **kwargs):
        response = requests.delete(self.get_url(endpoint), headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.status_code
