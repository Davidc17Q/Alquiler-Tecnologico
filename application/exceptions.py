from __future__ import annotations


class ApplicationError(Exception):
    """Excepción base de la capa de aplicación."""


class NotFoundError(ApplicationError):
    """Se lanza cuando una entidad requerida no existe."""


class BusinessRuleViolation(ApplicationError):
    """Se lanza cuando se viola una regla de negocio."""


class ConflictError(ApplicationError):
    """Se lanza cuando hay un conflicto de estado (ej. recurso ya usado)."""


class PaymentError(ApplicationError):
    """Se lanza cuando se produce un fallo al procesar un pago."""


class ValidationError(ApplicationError):
    """Se lanza ante datos de entrada coherentes a nivel de formato,
    pero inválidos a nivel de reglas de negocio (ej. fechas incoherentes).
    """


class AuthenticationError(ApplicationError):
    """Se lanza cuando la petición requiere sesión y no está autenticada."""


class ForbiddenError(ApplicationError):
    """Se lanza cuando el usuario no tiene permisos para la acción."""

