# services/pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from core.config import settings
from core.models import PurchaseOrder

def generate_po_pdf(po: PurchaseOrder, file_path: str):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 30*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, y, f"Purchase Order: {po.po_number}")
    y -= 10*mm
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, settings.COMPANY_NAME)
    y -= 6*mm
    c.drawString(20*mm, y, settings.COMPANY_ADDRESS)
    y -= 6*mm
    c.drawString(20*mm, y, f"Phone: {settings.COMPANY_PHONE}  Email: {settings.COMPANY_EMAIL}")
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, f"Supplier ID: {po.supplier_id}")
    y -= 8*mm
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, y, f"Order Date: {po.order_date.strftime('%Y-%m-%d')}   Status: {po.status.value}")
    y -= 10*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20*mm, y, "Item")
    c.drawString(90*mm, y, "Qty")
    c.drawString(110*mm, y, "Unit Cost")
    c.drawString(140*mm, y, "Line Total")
    y -= 6*mm
    c.setFont("Helvetica", 10)
    for ln in po.lines:
        if y < 30*mm:
            c.showPage()
            y = height - 30*mm
        c.drawString(20*mm, y, f"{ln.item.name} ({ln.item.sku})")
        c.drawRightString(105*mm, y, f"{ln.qty:.2f}")
        c.drawRightString(135*mm, y, f"{ln.unit_cost:.2f}")
        c.drawRightString(180*mm, y, f"{ln.line_total:.2f}")
        y -= 6*mm
    y -= 8*mm
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(180*mm, y, f"Subtotal: {po.subtotal:.2f}")
    y -= 6*mm
    c.drawRightString(180*mm, y, f"Tax: {po.tax:.2f}")
    y -= 6*mm
    c.drawRightString(180*mm, y, f"Total: {po.total:.2f}")
    c.showPage()
    c.save()
