# app/pages/08_Admin.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import User
from services.auth import role_allows, hash_password

def page():
    st.title("Admin")
    if not role_allows(["Admin"]):
        st.warning("Admins only")
        return
    db: Session = SessionLocal()
    st.subheader("Create user")
    with st.form("user_form"):
        username = st.text_input("Username")
        name = st.text_input("Name")
        email = st.text_input("Email")
        role = st.selectbox("Role", ["Admin","Storekeeper","Approver","Viewer"])
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Create/Update")
        if submitted:
            user = db.query(User).filter(User.username == username).first() or User(username=username)
            user.name = name; user.email = email; user.role = role; user.password_hash = hash_password(password)
            db.add(user); db.commit(); st.success("User saved")
    st.subheader("Users")
    st.dataframe([{"username": u.username, "role": u.role, "email": u.email, "active": u.is_active} for u in db.query(User).all()])
    db.close()

if __name__ == "__main__":
    page()
