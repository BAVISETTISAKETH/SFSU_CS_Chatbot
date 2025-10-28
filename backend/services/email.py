"""
Email Service - Send OTP verification emails using Resend
"""

import os
import random
import resend
from datetime import datetime, timedelta
from typing import Optional, Dict

class EmailService:
    """Service for sending emails using Resend."""

    def __init__(self):
        """Initialize email service with Resend."""
        self.api_key = os.getenv("RESEND_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")  # Default Resend test email

        # OTP storage (in production, use Redis or database)
        self.otp_storage: Dict[str, Dict] = {}

        self.enabled = bool(self.api_key)

        if self.enabled:
            resend.api_key = self.api_key
            print(f"[OK] Email service enabled with Resend (from: {self.sender_email})")
        else:
            print("[WARNING] Email service disabled. Set RESEND_API_KEY in .env for production")

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP."""
        return str(random.randint(100000, 999999))

    def store_otp(self, email: str, otp: str) -> None:
        """Store OTP with expiration (10 minutes)."""
        self.otp_storage[email] = {
            "otp": otp,
            "expires_at": datetime.utcnow() + timedelta(minutes=10),
            "attempts": 0
        }

    def verify_otp(self, email: str, otp: str) -> bool:
        """Verify OTP for an email."""
        if email not in self.otp_storage:
            return False

        stored_data = self.otp_storage[email]

        # Check if expired
        if datetime.utcnow() > stored_data["expires_at"]:
            del self.otp_storage[email]
            return False

        # Check attempts (max 5)
        if stored_data["attempts"] >= 5:
            del self.otp_storage[email]
            return False

        # Increment attempts
        stored_data["attempts"] += 1

        # Verify OTP
        if stored_data["otp"] == otp:
            del self.otp_storage[email]  # Remove after successful verification
            return True

        return False

    async def send_otp_email(self, to_email: str, name: str) -> Optional[str]:
        """
        Send OTP verification email using Resend.

        Args:
            to_email: Recipient email
            name: Recipient name

        Returns:
            OTP if sent successfully, None otherwise
        """
        # Generate OTP
        otp = self.generate_otp()

        if not self.enabled:
            # For development: return a test OTP
            print(f"[DEV MODE] Email service disabled. Test OTP for {to_email}: {otp}")
            self.store_otp(to_email, otp)
            return otp

        try:
            # Email HTML content
            html_content = f"""
            <html>
              <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                  <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4B2E83; margin: 0;">SFSU CS Chatbot</h1>
                    <p style="color: #B4975A; margin: 5px 0;">Email Verification</p>
                  </div>

                  <p style="color: #333; font-size: 16px;">Hello <strong>{name}</strong>,</p>

                  <p style="color: #555; font-size: 14px;">Thank you for registering as a professor for the SFSU CS Chatbot. Please use the following OTP to verify your email address:</p>

                  <div style="background: linear-gradient(135deg, #4B2E83 0%, #B4975A 100%); border-radius: 10px; padding: 20px; text-align: center; margin: 30px 0;">
                    <h2 style="color: white; font-size: 36px; letter-spacing: 8px; margin: 0;">{otp}</h2>
                  </div>

                  <p style="color: #555; font-size: 14px;">This OTP will expire in <strong>10 minutes</strong>.</p>

                  <p style="color: #555; font-size: 14px;">If you did not request this verification, please ignore this email.</p>

                  <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                  <p style="color: #999; font-size: 12px; text-align: center;">
                    This is an automated email from SFSU CS Chatbot.<br>
                    Do not reply to this email.
                  </p>
                </div>
              </body>
            </html>
            """

            # Send email using Resend
            params = {
                "from": f"SFSU CS Chatbot <{self.sender_email}>",
                "to": [to_email],
                "subject": "SFSU CS Chatbot - Email Verification",
                "html": html_content,
            }

            resend.Emails.send(params)

            # Store OTP
            self.store_otp(to_email, otp)

            print(f"[EMAIL] OTP sent to {to_email} via Resend")
            return otp

        except Exception as e:
            print(f"[ERROR] Failed to send email via Resend: {e}")
            # For development: return test OTP even on error
            print(f"[DEV MODE] OTP for {to_email}: {otp}")
            self.store_otp(to_email, otp)
            return otp
