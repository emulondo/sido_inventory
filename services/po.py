# services/po.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import Dict, List
from core.models import Item, Supplier, PurchaseOrder, PurchaseOrderLine, POStatus
from .stock import should_reorder, suggest_order_qty

def next_po_number(db: Session) -> str:
    num = db.query(func.count(PurchaseOrder.id)).scalar() or 0
    return f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{num+1:04d}"

def generate_draft_pos(db: Session, created_by: str = "system") -> List[int]:
    # Group items below reorder threshold by supplier
    items = db.query(Item).filter(Item.is_active == True).all()
    grouped: Dict[int, List[Item]] = {}
    for it in items:
        if should_reorder(db, it) and it.supplier_id:
            grouped.setdefault(it.supplier_id, []).append(it)

    created_ids = []
    for supplier_id, group_items in grouped.items():
        po = PurchaseOrder(
            po_number=next_po_number(db),
            supplier_id=supplier_id,
            status=POStatus.DRAFT,
            order_date=datetime.utcnow(),
            created_by=created_by,
        )
        db.add(po)
        db.flush()
        subtotal = 0.0
        for it in group_items:
            qty = suggest_order_qty(db, it)
            if qty <= 0:
                continue
            line_total = (it.unit_cost or 0.0) * qty
            db.add(PurchaseOrderLine(purchase_order_id=po.id, item_id=it.id, qty=qty, unit_cost=it.unit_cost or 0.0, line_total=line_total))
            subtotal += line_total
        po.subtotal = subtotal
        po.tax = round(subtotal * 0.18, 2)  # 18% VAT (adjust as needed)
        po.total = round(subtotal + po.tax, 2)
        db.commit()
        created_ids.append(po.id)
    return created_ids
