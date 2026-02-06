class DomainError(Exception):
    """Base class for domain errors"""


class ValidationError(DomainError):
    """Raised when data validation fails"""


class UnauthorizedError(DomainError):
    """Raised when authentication or authorization fails"""


class WorkspaceNotFoundError(DomainError):
    """Raised when a workspace is not found"""


class MemberNotFoundError(DomainError):
    """Raised when a member is not found"""


class NotFoundError(DomainError):
    """Raised when a resource is not found"""


class ConflictError(DomainError):
    """Raised when a resource already exists"""
