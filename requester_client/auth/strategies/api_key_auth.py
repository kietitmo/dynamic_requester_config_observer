from requester_client.auth.auth_strategy import AuthStrategy

class APIKeyAuth(AuthStrategy):
    def __init__(self, key: str, header_name: str = "X-API-Key"):
        self.key = key
        self.header_name = header_name

    def apply(self, headers: dict) -> dict:
        headers[self.header_name] = self.key
        return headers