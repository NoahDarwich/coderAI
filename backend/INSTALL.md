# Backend Installation Guide

## Quick Installation (Copy-Paste Commands)

### Step 1: Navigate to Backend Directory
```bash
cd /home/noahdarwich/code/coderAI/backend
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 6: Verify Installation (No Database Required)
```bash
python test_basic.py
```

If you see "🎉 All basic tests passed!" then installation was successful!

---

## Alternative: One-Line Install

```bash
cd /home/noahdarwich/code/coderAI/backend && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
```

Then test:
```bash
python test_basic.py
```

---

## What Gets Installed

- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **OpenAI** - LLM integration
- **LangChain** - LLM orchestration
- **Pandas** - Data processing
- **AsyncPG** - PostgreSQL driver
- **Alembic** - Database migrations
- And more...

---

## Troubleshooting

**If you get "python3: command not found":**
```bash
# Try 'python' instead
python -m venv venv
```

**If you get permission errors:**
```bash
# Make sure you're in the right directory
pwd
# Should show: /home/noahdarwich/code/coderAI/backend
```

**If installation is too slow:**
```bash
# Install with no cache (faster but uses more bandwidth)
pip install --no-cache-dir -r requirements.txt
```

**To start fresh (if something went wrong):**
```bash
rm -rf venv
# Then repeat steps 2-5
```

---

## Next Steps After Installation

1. **Configure environment** (optional for testing):
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

2. **Set up PostgreSQL** (only needed for full API testing):
   ```bash
   # Using Docker (easiest)
   docker run --name postgres-dev \
     -e POSTGRES_PASSWORD=devpass \
     -e POSTGRES_DB=data_extraction \
     -p 5432:5432 -d postgres:15
   ```

3. **Run migrations** (only after database setup):
   ```bash
   alembic upgrade head
   ```

4. **Start the server**:
   ```bash
   uvicorn src.main:app --reload
   ```

5. **Open API docs**: http://localhost:8000/docs

---

## Deactivate Virtual Environment

When you're done working:
```bash
deactivate
```

To reactivate later:
```bash
cd /home/noahdarwich/code/coderAI/backend
source venv/bin/activate
```
