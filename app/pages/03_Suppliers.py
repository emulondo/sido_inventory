# app/pages/03_Suppliers.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Supplier
from services.auth import role_allows

def page():
    st.title("Suppliers")
    db: Session = SessionLocal()
    if role_allows(["Admin", "Storekeeper"]):
        with st.form("supplier_form"):
            name = st.text_input("Name")
            contact_person = st.text_input("Contact Person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_area("Address")
            terms = st.text_input("Payment Terms", "30 days")
            submitted = st.form_submit_button("Save Supplier")
            if submitted:
                sp = db.query(Supplier).filter(Supplier.name == name).first() or Supplier(name=name)
                sp.contact_person = contact_person; sp.phone = phone; sp.email = email; sp.address = address; sp.payment_terms = terms
                db.add(sp); db.commit()
                st.success("Saved supplier")
    st.dataframe([{"name": s.name, "phone": s.phone, "email": s.email, "terms": s.payment_terms} for s in db.query(Supplier).all()])
    db.close()

if __name__ == "__main__":
    page()
