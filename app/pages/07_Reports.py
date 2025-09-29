# app/pages/07_Reports.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Item
from services.reports import stock_card, valuation_report

def page():
    st.title("Reports")
    db: Session = SessionLocal()
    items = db.query(Item).all()
    if not items:
        st.info("No items yet.")
        return
    mapping = {f"{it.name} ({it.sku})": it.id for it in items}
    label = st.selectbox("Stock card for item", list(mapping.keys()))
    df = stock_card(db, mapping[label])
    st.dataframe(df)
    st.download_button("Download stock card CSV", df.to_csv(index=False).encode("utf-8"), file_name="stock_card.csv")

    st.subheader("Valuation")
    val = valuation_report(db)
    st.dataframe(val)
    st.download_button("Download valuation CSV", val.to_csv(index=False).encode("utf-8"), file_name="valuation.csv")
    db.close()

if __name__ == "__main__":
    page()
