from requester_client.auth.auth_strategy import AuthStrategy

class BearerAuth(AuthStrategy):
    def __init__(self, token: str):
        self.token = token

    def apply(self, headers: dict) -> dict:
        headers["Authorization"] = f"Bearer {self.token}"
        return headers
