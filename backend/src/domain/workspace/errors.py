from src.domain.errors import DomainError


class WorkspaceNotFoundError(DomainError):
    pass


class MemberNotFoundError(DomainError):
    pass
