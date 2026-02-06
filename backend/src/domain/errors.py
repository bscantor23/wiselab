class DomainError(Exception):
    """Base class for domain errors"""
    pass


class ValidationError(DomainError):
    """Raised when data validation fails"""
    pass


class UnauthorizedError(DomainError):
    """Raised when authentication or authorization fails"""
    pass


class WorkspaceNotFoundError(DomainError):
    """Raised when a workspace is not found"""
    pass


class MemberNotFoundError(DomainError):
    """Raised when a member is not found"""
    pass


class NotFoundError(DomainError):
    """Raised when a resource is not found"""
    pass
