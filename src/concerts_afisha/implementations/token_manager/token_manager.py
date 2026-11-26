from typing import Final

import jwt

from concerts_afisha.interfaces.token_manager import TokenManager

from . import token_manager_errors


class JwtTokenManager(TokenManager):
    ALGORITHM: Final[str] = "HS256" # Fixed algorithm

    def __init__(
        self,
        secret_key: str,
    ) -> None:
        self._secret_key = secret_key

    def create_token(self, login: str) -> str:
        payload = {"sub": login}
        return jwt.encode(
            payload,
            self._secret_key,
            algorithm=self.ALGORITHM,
        )

    def get_login_from_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self.ALGORITHM],
            )
        except jwt.PyJWTError as exc:
            raise token_manager_errors.InvalidTokenError from exc
        
        login = payload.get("sub")
        if not isinstance(login, str) or not login:
            raise token_manager_errors.InvalidTokenError
        
        return login
