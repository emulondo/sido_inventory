# services/auth.py
import streamlit as st
import streamlit_authenticator as stauth
from typing import Dict
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def build_authenticator():
    # Demo users (passwords: admin123, store123, approve123)
    credentials = {
        "usernames": {
            "admin": {
                "email": "admin@sidps.com",
                "name": "Administrator",
                "password": "$2b$12$w9y6eKQv6e6yQXn1iV8o5u8x5sT8fCw0p6qT3o1xT9z2o8qT1k9zO",  # bcrypt for 'admin123'
                "role": "Admin"
            },
            "store": {
                "email": "store@sidps.com",
                "name": "Store Keeper",
                "password": "$2b$12$L6S7S6m3S4xYpV8K7eF9tOeS5c1Eo7B2s3N4pQ5rT6uY7iJ8kL9m.",  # bcrypt for 'store123'
                "role": "Storekeeper"
            },
            "approver": {
                "email": "approver@sidps.com",
                "name": "Approver",
                "password": "$2b$12$eT3o9L5mQ2rX6yB8nH4dWuJH8fK3lP6oS1dE2tV7wZ9xC0aB3cDHe",  # bcrypt for 'approve123'
                "role": "Approver"
            },
            "viewer": {
                "email": "viewer@sidps.com",
                "name": "Viewer",
                "password": "$2b$12$gkWzYyJ7Qf6t8f8iYqk1xOQj1aG3rV5lN0mP2sR4tU6vW8xY0zA2B.",  # bcrypt for 'viewer123'
                "role": "Viewer"
            },
        }
    }
    authenticator = stauth.Authenticate(credentials, "sido_inventory", "abcdef", cookie_expiry_days=7)
    return authenticator, credentials

def role_allows(required_roles):
    current_role = st.session_state.get("role", "Viewer")
    return current_role in required_roles
