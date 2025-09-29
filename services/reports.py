# services/reports.py
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from core.models import StockMovement, MovementType, Item

def stock_card(db: Session, item_id: int):
    rows = db.query(StockMovement).filter(StockMovement.item_id == item_id).order_by(StockMovement.timestamp.asc()).all()
    balance = 0.0
    data = []
    for r in rows:
        in_qty = r.qty if r.movement_type in (MovementType.PURCHASE, MovementType.ADJUSTMENT_PLUS, MovementType.RETURN) else 0.0
        out_qty = r.qty if r.movement_type in (MovementType.ISSUE, MovementType.ADJUSTMENT_MINUS) else 0.0
        balance += in_qty - out_qty
        data.append({
            "date": r.timestamp.strftime("%Y-%m-%d"),
            "type": r.movement_type.value,
            "ref": r.ref_doc or "",
            "in": in_qty,
            "out": out_qty,
            "balance": balance,
            "notes": r.notes or "",
        })
    return pd.DataFrame(data)

def valuation_report(db: Session):
    items = db.query(Item).all()
    rows = []
    from .stock import on_hand
    for it in items:
        bal = on_hand(db, it.id)
        value = round(bal * (it.unit_cost or 0.0), 2)
        rows.append({"sku": it.sku, "name": it.name, "on_hand": bal, "unit_cost": it.unit_cost or 0.0, "value": value})
    return pd.DataFrame(rows)
