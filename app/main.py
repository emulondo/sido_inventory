# app/main.py
import streamlit as st
from core.db import engine, Base, SessionLocal
from services.auth import build_authenticator
from core.config import settings

st.set_page_config(page_title=settings.APP_NAME, layout="wide")

# Ensure tables exist
Base.metadata.create_all(bind=engine)

st.title(settings.APP_NAME)
st.caption("Inventory tracking for purchases, issues, balances, reorder levels & POs")

authenticator, credentials = build_authenticator()
name, auth_status, username = authenticator.login("Login", "main")

if auth_status:
    st.sidebar.success(f"Logged in as {name}")
    st.session_state["role"] = credentials["usernames"][username]["role"]
    authenticator.logout("Logout", "sidebar")
    st.write("Use the pages on the left to navigate.")
elif auth_status is False:
    st.error("Invalid username/password")
else:
    st.info("Please log in to continue.")
