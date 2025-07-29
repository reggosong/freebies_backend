from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.schemas import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse, EmailResponse
from app.services.email_service import create_reset_token, verify_reset_token, send_password_reset_email
from app.utils import get_password_hash
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["password-reset"])

@router.post("/forgot-password", response_model=EmailResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset"""
    try:
        logger.info(f"Password reset requested for email: {request.email}")
        
        # Check if user exists
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.info(f"Password reset requested for non-existent email: {request.email}")
            # Don't reveal if email exists or not for security
            return EmailResponse(message="If the email exists, a password reset link has been sent.")
        
        # Create reset token
        token = create_reset_token(request.email)
        logger.info(f"Reset token created for user: {user.username}")
        
        # Store reset token in database
        reset_record = PasswordReset(
            email=request.email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1),
            used=False
        )
        db.add(reset_record)
        db.commit()
        logger.info(f"Reset token stored in database for: {request.email}")
        
        # Send email
        try:
            await send_password_reset_email(request.email, token)
            logger.info(f"Password reset email sent successfully to: {request.email}")
            return EmailResponse(message="If the email exists, a password reset link has been sent.")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {request.email}: {e}")
            # Remove the reset record if email fails
            db.delete(reset_record)
            db.commit()
            logger.error(f"Removed reset record due to email failure for: {request.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send password reset email: {str(e)}"
            )
    except Exception as e:
        logger.error(f"Unexpected error in forgot_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token"""
    try:
        # Verify token
        email = verify_reset_token(request.token)
        
        # Check if reset record exists and is valid
        reset_record = db.query(PasswordReset).filter(
            PasswordReset.token == request.token,
            PasswordReset.used == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update user password
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.hashed_password = get_password_hash(request.new_password)
        
        # Mark reset token as used
        reset_record.used = True
        
        db.commit()
        
        return PasswordResetResponse(message="Password has been reset successfully")
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        ) 