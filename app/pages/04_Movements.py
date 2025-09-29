# app/pages/04_Movements.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Item, StockMovement, MovementType
from services.auth import role_allows
from services.stock import on_hand

def page():
    st.title("Movements (Purchase / Issue / Adjustments)")
    if not role_allows(["Admin", "Storekeeper"]):
        st.warning("You do not have permission to record movements.")
        return
    db: Session = SessionLocal()
    items = db.query(Item).all()
    item_names = {f"{it.name} ({it.sku})": it for it in items}
    with st.form("mov"):
        item_label = st.selectbox("Item", list(item_names.keys()))
        it = item_names[item_label]
        mtype = st.selectbox("Type", [t.value for t in MovementType])
        qty = st.number_input("Quantity", 0.0, step=1.0)
        unit_cost = st.number_input("Unit Cost (for purchases)", 0.0, step=0.01)
        ref_doc = st.text_input("Reference (GRN/JobCard)")
        notes = st.text_area("Notes / Reason")
        submitted = st.form_submit_button("Record")
        if submitted:
            if mtype in [MovementType.ISSUE.value, MovementType.ADJUSTMENT_MINUS.value]:
                bal = on_hand(db, it.id)
                if qty > bal and not role_allows(["Admin"]):
                    st.error(f"Insufficient stock. On hand: {bal}")
                    db.close(); return
            mov = StockMovement(item_id=it.id, movement_type=MovementType(mtype), qty=qty, unit_cost=unit_cost, ref_doc=ref_doc, performed_by=st.session_state.get("role","user"), notes=notes)
            db.add(mov); db.commit()
            st.success("Movement recorded.")
    st.subheader("Recent Movements")
    ms = db.query(StockMovement).order_by(StockMovement.timestamp.desc()).limit(50).all()
    st.dataframe([{"date": m.timestamp, "item": m.item.name, "type": m.movement_type.value, "qty": m.qty, "ref": m.ref_doc} for m in ms])
    db.close()

if __name__ == "__main__":
    page()
