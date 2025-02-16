from machine.invoice_signer_ddd.domain.models.auth import Session
from typing import Optional


class SessionRepository:
    def save(self, session: Session) -> None:
        # Implementation for saving session
        pass

    def find_by_id(self, session_id: str) -> Optional[Session]:
        # Implementation for finding session
        pass

    def delete(self, session_id: str) -> None:
        # Implementation for deleting session
        pass
