"""
Validación de webhooks de Meta.
Implementa verificación de firma HMAC SHA256 según documentación oficial.
"""
import hmac
import hashlib
from fastapi import HTTPException, status
from config import settings
from utils.logger import app_logger


def verify_webhook_signature(payload: bytes, signature_header: str) -> bool:
    """
    Verifica la firma del webhook usando HMAC SHA256.
    
    Meta envía la firma en el header X-Hub-Signature-256 con formato:
    sha256=<hash>
    
    Args:
        payload: Cuerpo de la petición en bytes
        signature_header: Valor del header X-Hub-Signature-256
        
    Returns:
        True si la firma es válida, False en caso contrario
    """
    if not signature_header:
        app_logger.warning("Webhook recibido sin firma")
        return False
    
    # Extraer el hash de la firma (formato: sha256=<hash>)
    try:
        method, signature = signature_header.split("=")
        if method != "sha256":
            app_logger.error(f"Método de firma no soportado: {method}")
            return False
    except ValueError:
        app_logger.error(f"Formato de firma inválido: {signature_header}")
        return False
    
    # Calcular el hash esperado usando el app secret
    expected_signature = hmac.new(
        key=settings.meta_app_secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Comparación segura contra timing attacks
    is_valid = hmac.compare_digest(expected_signature, signature)
    
    if not is_valid:
        app_logger.warning("Firma de webhook inválida")
    
    return is_valid


def validate_verify_token(token: str) -> bool:
    """
    Valida el verify token en la petición de verificación GET.
    
    Args:
        token: Token recibido en el parámetro hub.verify_token
        
    Returns:
        True si el token coincide con el configurado
    """
    is_valid = token == settings.meta_verify_token
    
    if not is_valid:
        app_logger.warning(f"Verify token inválido recibido: {token}")
    
    return is_valid


def verify_webhook_request(payload: bytes, signature: str) -> None:
    """
    Verifica un webhook y lanza excepción si no es válido.
    
    Args:
        payload: Cuerpo de la petición
        signature: Header X-Hub-Signature-256
        
    Raises:
        HTTPException: Si la firma no es válida
    """
    if not verify_webhook_signature(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Firma de webhook inválida"
        )