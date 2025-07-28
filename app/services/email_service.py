from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import get_settings
from pathlib import Path
import jwt
from datetime import datetime, timedelta

settings = get_settings()

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'email_templates'
)

fastmail = FastMail(conf)

def create_reset_token(email: str) -> str:
    """Create a JWT token for password reset"""
    expiration = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    payload = {
        "email": email,
        "exp": expiration,
        "type": "password_reset"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_reset_token(token: str) -> str:
    """Verify and decode the reset token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            raise ValueError("Invalid token type")
        return payload.get("email")
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

async def send_password_reset_email(email: str, token: str):
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password for the Freebies app.</p>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    Reset Password
                </a>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <p>Best regards,<br>The Freebies Team</p>
            </body>
        </html>
        """,
        subtype="html"
    )
    
    await fastmail.send_message(message) 