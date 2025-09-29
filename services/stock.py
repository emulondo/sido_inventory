# services/stock.py
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timedelta
import math
from typing import Tuple, Optional
from core.models import StockMovement, MovementType, Item
from core.config import settings

def on_hand(db: Session, item_id: int) -> float:
    plus = db.query(func.coalesce(func.sum(StockMovement.qty), 0.0)).filter(
        StockMovement.item_id == item_id,
        StockMovement.movement_type.in_([MovementType.PURCHASE, MovementType.ADJUSTMENT_PLUS, MovementType.RETURN])
    ).scalar()
    minus = db.query(func.coalesce(func.sum(StockMovement.qty), 0.0)).filter(
        StockMovement.item_id == item_id,
        StockMovement.movement_type.in_([MovementType.ISSUE, MovementType.ADJUSTMENT_MINUS])
    ).scalar()
    return float(plus - minus)

def usage_series(db: Session, item_id: int, days: int) -> list:
    start = datetime.utcnow() - timedelta(days=days)
    rows = db.query(StockMovement.timestamp, StockMovement.qty).filter(
        StockMovement.item_id == item_id,
        StockMovement.movement_type == MovementType.ISSUE,
        StockMovement.timestamp >= start
    ).all()
    # Aggregate by day
    buckets = {}
    for ts, qty in rows:
        key = ts.date()
        buckets[key] = buckets.get(key, 0.0) + float(qty)
    return list(buckets.values())

def compute_avg_daily_usage(db: Session, item_id: int, days: int = None) -> float:
    if days is None:
        days = settings.USAGE_WINDOW_DAYS
    series = usage_series(db, item_id, days)
    if not series:
        return 0.0
    return sum(series) / max(len(series), 1)

def compute_std_daily_usage(db: Session, item_id: int, days: int = None) -> float:
    if days is None:
        days = settings.USAGE_WINDOW_DAYS
    series = usage_series(db, item_id, days)
    n = len(series)
    if n <= 1:
        return 0.0
    mean = sum(series) / n
    var = sum((x - mean) ** 2 for x in series) / (n - 1)
    return math.sqrt(var)

def compute_reorder_point(db: Session, item: Item) -> float:
    avg = compute_avg_daily_usage(db, item.id)
    std = compute_std_daily_usage(db, item.id)
    z = settings.SERVICE_LEVEL_Z
    safety = item.safety_stock if (item.safety_stock or 0) > 0 else z * std * math.sqrt(max(item.lead_time_days, 0))
    rop = (avg * max(item.lead_time_days, 0)) + safety
    return max(0.0, rop)

def should_reorder(db: Session, item: Item) -> bool:
    balance = on_hand(db, item.id)
    rop = compute_reorder_point(db, item)
    return balance <= rop or balance < (item.min_level or 0)

def suggest_order_qty(db: Session, item: Item) -> float:
    balance = on_hand(db, item.id)
    rop = compute_reorder_point(db, item)
    target = max(item.min_level or 0, rop)
    qty = (item.max_level or target) - balance
    return max(0.0, round(qty, 2))
