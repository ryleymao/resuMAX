import firebase_admin
from firebase_admin import credentials, auth
from functools import lru_cache
from app.core.config import get_settings


@lru_cache()
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    settings = get_settings()

    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'projectId': settings.FIREBASE_PROJECT_ID,
        })

    return firebase_admin.get_app()


async def verify_firebase_token(token: str) -> dict:
    """
    Verify Firebase ID token and return decoded claims

    Args:
        token: Firebase ID token from client

    Returns:
        Decoded token claims including uid, email, etc.

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid authentication token: {str(e)}")
