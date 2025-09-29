# app/pages/02_Items.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Item, Supplier
from services.auth import role_allows
from services.stock import on_hand

def page():
    st.title("Items")
    db: Session = SessionLocal()
    if role_allows(["Admin", "Storekeeper"]):
        with st.expander("Create / Edit Item"):
            sku = st.text_input("SKU")
            name = st.text_input("Name")
            category = st.text_input("Category", "Substrates")
            unit = st.text_input("Unit", "rolls")
            unit_cost = st.number_input("Unit Cost", 0.0, step=0.01)
            min_level = st.number_input("Min Level", 0.0, step=1.0)
            max_level = st.number_input("Max Level", 0.0, step=1.0)
            safety_stock = st.number_input("Safety Stock (override)", 0.0, step=1.0)
            lead_time_days = st.number_input("Lead Time (days)", 0, step=1, value=7)
            supplier = st.text_input("Default Supplier (name)")
            if st.button("Save Item"):
                sp = db.query(Supplier).filter(Supplier.name == supplier).first()
                it = db.query(Item).filter(Item.sku == sku).first()
                if not it:
                    it = Item(sku=sku, name=name)
                it.category = category; it.unit = unit; it.unit_cost = unit_cost
                it.min_level = min_level; it.max_level = max_level
                it.safety_stock = safety_stock; it.lead_time_days = lead_time_days
                if sp: it.supplier_id = sp.id
                db.add(it); db.commit()
                st.success("Saved")
    rows = []
    for it in db.query(Item).all():
        rows.append({"sku": it.sku, "name": it.name, "unit": it.unit, "on_hand": on_hand(db, it.id), "unit_cost": it.unit_cost})
    st.dataframe(rows)
    db.close()

if __name__ == "__main__":
    page()
