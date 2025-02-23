class MachineException(Exception):
    """Base class for all machine exceptions"""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NoPinFoundException(MachineException):
    """Exception raised when a PIN is not found in environment variables"""

    def __init__(self, env_var: str):
        self.env_var = env_var
        message = f"No PIN found in environment for variable: {env_var}"
        super().__init__(message)


class USBNotFoundException(MachineException):
    """Exception raised when USB device is not found"""

    def __init__(self, message: str = "USB device not found"):
        super().__init__(message)


class CertificateNotFoundException(Exception):
    """Exception raised when certificate is not found"""

    def __init__(self, idno: str):
        super().__init__(f"Certificate with idno {idno} not found")


class LoginFailedException(Exception):
    """Exception raised when login fails"""

    def __init__(self, message: str = "Login failed"):
        super().__init__(message)


class NavigationException(Exception):
    """Exception raised when navigation fails"""

    def __init__(self, message: str = "Navigation failed"):
        super().__init__(message)


class IDNONotFoundException(Exception):
    """Exception raised when an IDNO is not found in the USB_PIN mapping"""

    def __init__(self, idno: str, message: str = None):
        self.idno = idno
        self.message = message or f"No USB PIN configured for IDNO: {idno}"
        super().__init__(self.message)
