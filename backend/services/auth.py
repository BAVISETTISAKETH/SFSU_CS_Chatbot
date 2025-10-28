"""
Authentication Service - Professor Login & JWT (SIMPLIFIED)
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from supabase import create_client, Client

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

class AuthService:
    """Service for professor authentication - SIMPLIFIED."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(supabase_url, supabase_key)

    async def authenticate_professor(self, username_or_email: str, password: str) -> Optional[Dict]:
        """
        SIMPLE authentication - plain text password comparison.
        """
        try:
            print(f"\n[AUTH] Login attempt for: {username_or_email}")

            # Try to find professor by username first
            result = self.client.table("professors").select("*").eq("username", username_or_email).execute()

            # If not found by username, try email
            if not result.data or len(result.data) == 0:
                print(f"[AUTH] Not found by username, trying email...")
                result = self.client.table("professors").select("*").eq("email", username_or_email).execute()

            if not result.data or len(result.data) == 0:
                print(f"[AUTH] FAILED - No professor found")
                return None

            professor = result.data[0]
            print(f"[AUTH] Found: {professor.get('name')} ({professor.get('email')})")
            print(f"[AUTH] Password from DB: '{professor.get('password_hash')}'")
            print(f"[AUTH] Password entered: '{password}'")

            # SIMPLE string comparison
            if professor.get("password_hash") == password:
                print(f"[AUTH] SUCCESS - Passwords match!")

                # Update last login
                self.client.table("professors").update({
                    "last_login": datetime.utcnow().isoformat()
                }).eq("id", professor["id"]).execute()

                return {
                    "id": professor["id"],
                    "email": professor["email"],
                    "username": professor.get("username"),
                    "name": professor["name"],
                    "department": professor["department"]
                }
            else:
                print(f"[AUTH] FAILED - Passwords don't match")
                return None

        except Exception as e:
            print(f"[AUTH ERROR] {str(e)}")
            return None

    def create_access_token(self, data: Dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
