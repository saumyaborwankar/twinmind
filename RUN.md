# How to Run Second Brain

## Option 1: Automated Setup (Recommended - 2 minutes)

```bash
# 1. Run the setup script
./setup.sh

# 2. Add your OpenAI API key to .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start the server
python -m app.main
```

Done! Server is running at http://localhost:8000

---

## Option 2: Manual Setup (5 minutes)

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit and add your OpenAI API key
nano .env  # or use any text editor
```

Your `.env` should look like:
```
OPENAI_API_KEY=sk-your-actual-key-here
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EMBEDDING_MODEL=text-embedding-3-large
```

### Step 4: Start the Server
```bash
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Testing Your Installation

### Quick Health Check
Open a new terminal and run:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "vector_db_count": 0,
  "database_documents": 0
}
```

### Interactive Test
```bash
# Make sure server is running, then:
source venv/bin/activate
python test_api.py
```

### View API Documentation
Open your browser: http://localhost:8000/docs

---

## Using the System

### Upload a PDF

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@/path/to/your/document.pdf"
```

**Using Python:**
```python
from example_usage import SecondBrainClient

client = SecondBrainClient()
result = client.upload_pdf("my_document.pdf")
print(f"Uploaded: {result['title']}")
```

### Search Documents

**Using curl:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

**Using Python:**
```python
results = client.search("machine learning", top_k=5)
for result in results['results']:
    print(f"{result['document_title']}: {result['content'][:100]}...")
```

---

## Common Issues

### "ModuleNotFoundError"
**Solution:** Activate virtual environment
```bash
source venv/bin/activate
```

### "OpenAI API Error"
**Solution:** Check your API key in `.env`
```bash
# View current key
cat .env | grep OPENAI_API_KEY

# Set new key
echo "OPENAI_API_KEY=sk-your-new-key" >> .env
```

### "Port already in use"
**Solution:** Change port or kill existing process
```bash
# Option 1: Change port in .env
echo "API_PORT=8001" >> .env

# Option 2: Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### "Connection refused"
**Solution:** Make sure server is running
```bash
python -m app.main
```

---

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Next Steps

1. **Upload PDFs:** Use the test script or API
2. **Try Searches:** Experiment with different queries
3. **Read Docs:** Check [GETTING_STARTED.md](GETTING_STARTED.md)
4. **Explore API:** Visit http://localhost:8000/docs

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `./setup.sh` | Automated setup |
| `source venv/bin/activate` | Activate environment |
| `python -m app.main` | Start server |
| `python test_api.py` | Run tests |
| `curl http://localhost:8000/api/health` | Health check |

**API Docs:** http://localhost:8000/docs

**Need Help?** See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed guide.
