from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import get_settings
from pathlib import Path
import jwt
from datetime import datetime, timedelta
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create email_templates directory if it doesn't exist
template_folder = Path(__file__).parent / 'email_templates'
template_folder.mkdir(exist_ok=True)

# Email configuration
try:
    conf = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        TEMPLATE_FOLDER=template_folder
    )
    fastmail = FastMail(conf)
    logger.info(f"Email service configured with server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
except Exception as e:
    logger.error(f"Failed to configure email service: {e}")
    fastmail = None

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
    # Create a deep link for the React Native app using Expo format
    # This will work with Expo Go and development builds
    reset_url = f"exp://192.168.1.248:8081/--/reset-password?token={token}"
    
    # Fallback URL for testing
    fallback_url = f"freebies://reset-password?token={token}"

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
                <p><strong>If the link above doesn't work, try this alternative link:</strong></p>
                <a href="{fallback_url}" style="background-color: #2196F3; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 10px;">
                    Alternative Reset Link
                </a>
                <p style="margin-top: 20px; font-size: 12px; color: #666;">
                    <strong>Manual URL (copy and paste):</strong><br>
                    {reset_url}
                </p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this password reset, please ignore this email.</p>
                <p>Best regards,<br>The Freebies Team</p>
            </body>
        </html>
        """,
        subtype="html"
    )

    try:
        if fastmail:
            await fastmail.send_message(message)
            logger.info(f"Password reset email sent successfully to {email}")
        else:
            # Fallback: log the email details instead of sending
            logger.warning(f"Email service not available. Would send reset email to {email} with token: {token}")
            logger.warning(f"Reset URL: {reset_url}")
            raise Exception("Email service not configured properly")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email}: {e}")
        # Log the email details for debugging
        logger.error(f"Email details - To: {email}, Token: {token}, URL: {reset_url}")
        
        # TEMPORARY: Log the reset link to console for testing
        print(f"\n{'='*80}")
        print(f"🔗 PASSWORD RESET LINK (for testing):")
        print(f"Email: {email}")
        print(f"Reset URL: {reset_url}")
        print(f"Fallback URL: {fallback_url}")
        print(f"Token: {token}")
        print(f"{'='*80}\n")
        
        raise e 