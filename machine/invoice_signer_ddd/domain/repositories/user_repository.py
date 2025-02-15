from domain.models import User


class UserRepository:
    def find_by_idno(self, idno: str) -> User:
        raise NotImplementedError

    def save(self, user: User) -> None:
        raise NotImplementedError
