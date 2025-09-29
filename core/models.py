# core/models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .db import Base

class MovementType(str, enum.Enum):
    PURCHASE = "PURCHASE"
    ISSUE = "ISSUE"
    ADJUSTMENT_PLUS = "ADJUSTMENT_PLUS"
    ADJUSTMENT_MINUS = "ADJUSTMENT_MINUS"
    RETURN = "RETURN"

class POStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    sku = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(128), default="General")
    unit = Column(String(32), default="unit")
    unit_cost = Column(Float, default=0.0)
    min_level = Column(Float, default=0.0)
    max_level = Column(Float, default=0.0)
    reorder_point = Column(Float, default=0.0)
    safety_stock = Column(Float, default=0.0)
    lead_time_days = Column(Integer, default=7)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    barcode = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="items")
    movements = relationship("StockMovement", back_populates="item")

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    contact_person = Column(String(128), nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    payment_terms = Column(String(128), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("Item", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    qty = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)
    ref_doc = Column(String(128), nullable=True)
    performed_by = Column(String(128), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)

    item = relationship("Item", back_populates="movements")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    po_number = Column(String(64), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    status = Column(Enum(POStatus), default=POStatus.DRAFT, index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_date = Column(DateTime, nullable=True)
    created_by = Column(String(128), nullable=True)
    approved_by = Column(String(128), nullable=True)
    subtotal = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    qty = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False, default=0.0)
    line_total = Column(Float, nullable=False, default=0.0)

    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    item = relationship("Item")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    email = Column(String(128), nullable=True)
    role = Column(String(32), default="Viewer")  # Admin, Storekeeper, Approver, Viewer
    is_active = Column(Boolean, default=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user = Column(String(128), nullable=True)
    action = Column(String(64), nullable=False)
    entity = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=True)
    meta = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
