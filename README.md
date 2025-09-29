# SIDO Inventory (Streamlit + SQLite)

A minimal, production-ready starter for SIDO's print inventory: track purchases, issues, balances, reorder points, and generate draft purchase orders with a Streamlit UI.

## Features
- Items, Suppliers, Stock Movements
- On-hand balance, reorder logic (ROP + safety stock), suggested order qty
- Draft POs with PDF export
- Basic authentication (streamlit-authenticator) + simple RBAC in UI
- Reports (stock card, valuation)

> This is an MVP. You can extend RBAC, audit logging, Alembic migrations, Postgres, emailing, etc.

---

## 1) Run Locally (Windows PowerShell or macOS/Linux)

```bash
cd sido_inventory
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# First run: initialize DB and seed data
python seed.py

# Run the app
streamlit run app/main.py
```

Login demo users:
- admin / **admin123** (Admin)
- store / **store123** (Storekeeper)
- approver / **approve123** (Approver)
- viewer / **viewer123** (Viewer)

If you need to change settings, copy `.env.example` to `.env` and edit.

---

## 2) Project Layout
```
app/ (Streamlit UI pages)
core/ (config, db, models)
services/ (auth, stock logic, POs, pdf, reports)
data/ (SQLite file will appear here after first run)
seed.py
```

---

## 3) Deploy Options

### Option A: Streamlit Community Cloud (fastest)
1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io/ and connect repo.
3. Set the **Main file path** to `app/main.py`.
4. Add a **Secrets** section with your `.env` keys, e.g.:
```
APP_NAME="SIDO Inventory"
SECRET_KEY="a-very-random-string"
# For SQLite, no change needed. For Postgres, use a URL like:
# DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname"
```
5. Deploy.

### Option B: Railway/Render (managed containers)
1. Add a `Procfile` (optional):
```
web: streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0
```
2. Add environment variables as in `.env.example`.
3. Ensure a persistent volume for the `data/` directory if you want DB persistence.

### Option C: Docker (portable)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "app/main.py"]
```
Build & run:
```bash
docker build -t sido-inventory .
docker run -p 8501:8501 -v $(pwd)/data:/app/data --env-file .env sido-inventory
```

### Option D: Bare VM (Ubuntu 22.04 on DigitalOcean/AWS/GCP)
```bash
sudo apt update && sudo apt install -y python3-venv
git clone <your-repo-url> sido_inventory
cd sido_inventory
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed.py
# Open firewall for Streamlit
streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501
# Access via http://<server-ip>:8501
```

> For HTTPS, run behind Nginx reverse proxy or use a platform that provides TLS by default.

---

## 4) Switching to PostgreSQL
1. Provision a Postgres DB (Railway/Render/RDS).
2. Set `DATABASE_URL` to something like:
```
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
```
3. Install `psycopg2-binary` and update `requirements.txt`.
4. Create tables and migrate data (export from SQLite and import, or use Alembic in a future iteration).

---

## 5) Notes
- This starter enforces “no negative stock” for issues unless the user has Admin role.
- Safety stock defaults to `z * stddev(usage) * sqrt(lead_time)`. You can set per-item overrides.
- PDF PO generator uses reportlab and saves to `/mnt/data/PO-*.pdf` when run inside ChatGPT sandbox or `./` in your environment.
