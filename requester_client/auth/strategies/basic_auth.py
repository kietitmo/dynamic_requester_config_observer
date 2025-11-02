from requester_client.auth.auth_strategy import AuthStrategy
import base64

class BasicAuth(AuthStrategy):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def apply(self, headers: dict) -> dict:
        encoded = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"
        return headers
