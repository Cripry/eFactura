class USBNotFoundException(Exception):
    """Exception raised when USB device is not found"""

    def __init__(self, message: str = "USB device not found"):
        super().__init__(message)


class CertificateNotFoundException(Exception):
    """Exception raised when certificate is not found"""

    def __init__(self, idno: str):
        super().__init__(f"Certificate with IDNO {idno} not found")


class LoginFailedException(Exception):
    """Exception raised when login fails"""

    def __init__(self, message: str = "Login failed"):
        super().__init__(message)


class NavigationException(Exception):
    """Exception raised when navigation fails"""

    def __init__(self, message: str = "Navigation failed"):
        super().__init__(message)
