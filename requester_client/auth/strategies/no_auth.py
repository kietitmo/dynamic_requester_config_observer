
from requester_client.auth.auth_strategy import AuthStrategy

class NoAuth(AuthStrategy):
    def apply(self, headers: dict) -> dict:
        return headers
