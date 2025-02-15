from domain.models import Worker, Session


class AuthenticationService:
    def login(self, worker: Worker) -> Session:
        """Authenticate worker using their IDNO"""
        raise NotImplementedError

    def logout(self, session: Session) -> bool:
        """End the current session"""
        raise NotImplementedError
