# services/import_export.py
import pandas as pd
from sqlalchemy.orm import Session
from core.models import Item

def export_items(db: Session) -> pd.DataFrame:
    items = db.query(Item).all()
    rows = []
    for it in items:
        rows.append({
            "sku": it.sku,
            "name": it.name,
            "category": it.category,
            "unit": it.unit,
            "unit_cost": it.unit_cost,
            "min_level": it.min_level,
            "max_level": it.max_level,
            "reorder_point": it.reorder_point,
            "safety_stock": it.safety_stock,
            "lead_time_days": it.lead_time_days,
            "supplier_id": it.supplier_id,
            "barcode": it.barcode,
            "is_active": it.is_active,
        })
    return pd.DataFrame(rows)
