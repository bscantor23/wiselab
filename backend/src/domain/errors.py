class DomainError(Exception):
    """Base class for all domain errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class EntityNotFoundError(DomainError):
    """Raised when an entity is not found"""
    pass

class ValidationError(DomainError):
    """Raised when a domain validation fails"""
    pass

class UnauthorizedError(DomainError):
    """Raised when an operation is unauthorized"""
    pass
