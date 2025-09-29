# app/pages/06_Purchase_Orders.py
import streamlit as st
from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import PurchaseOrder, PurchaseOrderLine, POStatus, Item, StockMovement, MovementType
from services.auth import role_allows
from services.pdf import generate_po_pdf

def page():
    st.title("Purchase Orders")
    db: Session = SessionLocal()
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).all()
    st.dataframe([{"po_number": p.po_number, "status": p.status.value, "supplier_id": p.supplier_id, "total": p.total} for p in pos])

    if pos:
        with st.expander("Open PO"):
            sel = st.selectbox("Select PO", [p.po_number for p in pos])
            po = next(p for p in pos if p.po_number == sel)
            st.write(f"Status: {po.status.value}")
            st.table([{"item": ln.item.name, "qty": ln.qty, "unit_cost": ln.unit_cost, "line_total": ln.line_total} for ln in po.lines])
            if role_allows(["Approver", "Admin"]) and po.status.name in ["DRAFT","SUBMITTED"] and st.button("Approve"):
                po.status = POStatus.APPROVED; db.commit(); st.success("Approved")
            if role_allows(["Storekeeper","Admin"]) and po.status == POStatus.DRAFT and st.button("Submit"):
                po.status = POStatus.SUBMITTED; db.commit(); st.success("Submitted")
            if role_allows(["Storekeeper","Admin"]) and po.status == POStatus.APPROVED and st.button("Mark as Received"):
                for ln in po.lines:
                    db.add(StockMovement(item_id=ln.item_id, movement_type=MovementType.PURCHASE, qty=ln.qty, unit_cost=ln.unit_cost, ref_doc=po.po_number, performed_by="system"))
                po.status = POStatus.RECEIVED; db.commit(); st.success("Received and stock updated")
            if st.button("Download PDF"):
                path = f"/mnt/data/{po.po_number}.pdf"
                generate_po_pdf(po, path)
                st.download_button("Download PO PDF", data=open(path, "rb").read(), file_name=f"{po.po_number}.pdf")

    db.close()

if __name__ == "__main__":
    page()
