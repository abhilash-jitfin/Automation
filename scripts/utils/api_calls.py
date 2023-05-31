import threading

import requests


class SimpleRequests:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, token: str = None) -> None:
        """
        Initialize the SimpleRequests instance.

        Args:
            token: Authorization token (optional).
        """
        self.base_url = ApiConstants.BASE_URL
        self.headers = {}
        if token:
            self.set_token(token)

    @classmethod
    def get_instance(cls, token: str = None) -> "SimpleRequests":
        """
        Get the singleton instance of SimpleRequests.

        Args:
            token: Authorization token (optional).

        Returns:
            The SimpleRequests instance.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls(token)
        return cls._instance

    def set_token(self, token: str) -> None:
        """
        Set the authorization token.

        Args:
            token: Authorization token.
        """
        with self._lock:
            self.headers['Authorization'] = token

    def get_url(self, endpoint: str) -> str:
        """
        Get the complete URL for the given endpoint.

        Args:
            endpoint: API endpoint.

        Returns:
            Complete URL.
        """
        return self.base_url + endpoint

    def get(self, endpoint: str, **kwargs) -> dict:
        """
        Send a GET request to the specified endpoint.

        Args:
            endpoint: API endpoint.
            **kwargs: Additional request parameters.

        Returns:
            JSON response as a dictionary.
        """
        response = requests.get(self.get_url(endpoint), headers=self.headers, **kwargs)
        response.raise_for_status()
        return response

    def post(self, endpoint: str, data=None, **kwargs) -> dict:
        """
        Send a POST request to the specified endpoint.

        Args:
            endpoint: API endpoint.
            data: Request data (optional).
            **kwargs: Additional request parameters.

        Returns:
            JSON response as a dictionary.
        """
        response = requests.post(self.get_url(endpoint), data=data, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response

    def patch(self, endpoint: str, data=None, **kwargs) -> dict:
        """
        Send a PATCH request to the specified endpoint.

        Args:
            endpoint: API endpoint.
            data: Request data (optional).
            **kwargs: Additional request parameters.

        Returns:
            JSON response as a dictionary.
        """
        response = requests.patch(self.get_url(endpoint), data=data, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response

    def delete(self, endpoint: str, **kwargs) -> int:
        """
        Send a DELETE request to the specified endpoint.

        Args:
            endpoint: API endpoint.
            **kwargs: Additional request parameters.

        Returns:
            HTTP status code.
        """
        response = requests.delete(self.get_url(endpoint), headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.status_code


class ApiConstants:
    BASE_URL = "https://qa.appv2.kyss.ai/apis"
    OTP_ENDPOINT = "/accounts/signin/otp"
    VALIDATE_ENDPOINT = "/accounts/signin/otp/validate"
    PRE_REGISTER_FILE_UPLOAD_ENDPOINT = "/accounts/pre-register/file/upload"
