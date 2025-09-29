# app/pages/01_Dashboard.py
import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Item, StockMovement, MovementType
from services.stock import on_hand, should_reorder
from services.reports import valuation_report

def page():
    st.title("Dashboard")
    db: Session = SessionLocal()
    items = db.query(Item).all()
    below = [{"sku": it.sku, "name": it.name, "on_hand": on_hand(db, it.id)} for it in items if should_reorder(db, it)]
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Items needing reorder")
        st.dataframe(pd.DataFrame(below))
    with col2:
        st.subheader("Stock valuation")
        st.dataframe(valuation_report(db))
    db.close()

if __name__ == "__main__":
    page()
