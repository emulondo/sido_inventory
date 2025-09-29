# app/pages/05_Reorder_Suggestions.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Item, PurchaseOrder
from services.auth import role_allows
from services.stock import should_reorder, suggest_order_qty, on_hand
from services.po import generate_draft_pos

def page():
    st.title("Reorder Suggestions")
    db: Session = SessionLocal()
    items = db.query(Item).all()
    rows = []
    for it in items:
        if should_reorder(db, it):
            rows.append({
                "sku": it.sku, "name": it.name, "on_hand": on_hand(db, it.id),
                "suggest_qty": suggest_order_qty(db, it), "supplier_id": it.supplier_id
            })
    st.dataframe(rows)
    if role_allows(["Admin", "Storekeeper"]) and st.button("Generate DRAFT POs"):
        ids = generate_draft_pos(db, created_by=st.session_state.get("role", "user"))
        st.success(f"Created {len(ids)} draft PO(s). See Purchase Orders page.")
    db.close()

if __name__ == "__main__":
    page()
