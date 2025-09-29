# seed.py
from core.db import engine, Base, SessionLocal
from core.models import Supplier, Item, StockMovement, MovementType, User
from services.auth import hash_password
from datetime import datetime, timedelta
import random

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Suppliers
    supps = [
        Supplier(name="Rama Paper", contact_person="Grace", phone="+256700000001", email="sales@rama.com", payment_terms="30 days"),
        Supplier(name="InkWorks UG", contact_person="Abel", phone="+256700000002", email="info@inkworks.ug", payment_terms="15 days"),
        Supplier(name="PlateTech EA", contact_person="Joan", phone="+256700000003", email="hello@platetech.ea"),
    ]
    for s in supps: db.merge(s)
    db.commit()

    suppliers = db.query(Supplier).all()
    s_map = {s.name: s.id for s in suppliers}

    # Items
    items = [
        Item(sku="PAPER-SGA80", name="Semi-Gloss Adhesive 80g", category="Substrates", unit="rolls", unit_cost=120000.0, min_level=10, max_level=50, lead_time_days=7, supplier_id=s_map["Rama Paper"]),
        Item(sku="INK-CMYK-C", name="Cyan Ink", category="Inks", unit="liters", unit_cost=180000.0, min_level=5, max_level=20, lead_time_days=14, supplier_id=s_map["InkWorks UG"]),
        Item(sku="INK-CMYK-M", name="Magenta Ink", category="Inks", unit="liters", unit_cost=180000.0, min_level=5, max_level=20, lead_time_days=14, supplier_id=s_map["InkWorks UG"]),
        Item(sku="INK-CMYK-Y", name="Yellow Ink", category="Inks", unit="liters", unit_cost=180000.0, min_level=5, max_level=20, lead_time_days=14, supplier_id=s_map["InkWorks UG"]),
        Item(sku="INK-CMYK-K", name="Black Ink", category="Inks", unit="liters", unit_cost=180000.0, min_level=5, max_level=20, lead_time_days=14, supplier_id=s_map["InkWorks UG"]),
        Item(sku="PLATE-A3", name="Aluminium Plate A3", category="Plates", unit="pcs", unit_cost=35000.0, min_level=20, max_level=100, lead_time_days=5, supplier_id=s_map["PlateTech EA"]),
    ]
    for it in items: db.merge(it)
    db.commit()

    # Users
    users = [
        User(username="admin", name="Administrator", email="admin@sidps.com", role="Admin", password_hash=hash_password("admin123")),
        User(username="store", name="Store Keeper", email="store@sidps.com", role="Storekeeper", password_hash=hash_password("store123")),
        User(username="approver", name="Approver", email="approver@sidps.com", role="Approver", password_hash=hash_password("approve123")),
        User(username="viewer", name="Viewer", email="viewer@sidps.com", role="Viewer", password_hash=hash_password("viewer123")),
    ]
    for u in users: db.merge(u)
    db.commit()

    # Movements (synthetic 200 days)
    items = db.query(Item).all()
    start = datetime.utcnow() - timedelta(days=200)
    for day in range(200):
        ts = start + timedelta(days=day)
        # purchases occasionally
        if day % 15 == 0:
            for it in items:
                qty = random.choice([0, 0, 5, 10, 20])
                if qty:
                    db.add(StockMovement(item_id=it.id, movement_type=MovementType.PURCHASE, qty=qty, unit_cost=it.unit_cost, ref_doc="SEEDPO", performed_by="seed", timestamp=ts))
        # issues daily
        for it in items:
            qty = max(0, int(random.gauss(3, 1)))
            if qty:
                db.add(StockMovement(item_id=it.id, movement_type=MovementType.ISSUE, qty=qty, unit_cost=it.unit_cost, ref_doc="JOB", performed_by="seed", timestamp=ts))
    db.commit()
    db.close()
    print("Seed completed.")

if __name__ == "__main__":
    seed()
