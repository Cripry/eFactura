class MachineException(Exception):
    """Base class for all machine exceptions"""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class USBNotFoundException(MachineException):
    """Exception raised when USB device is not found"""
    def __init__(self, message: str = "USB device not found"):
        super().__init__(message) 