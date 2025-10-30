# Quick Start Guide

Get your Second Brain up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-...
```

## Step 3: Start the Server

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

## Step 4: Test the API

Open a new terminal and run:

```bash
python test_api.py
```

Or visit the interactive docs: http://localhost:8000/docs

## Step 5: Upload Your First PDF

### Using curl:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.pdf"
```

### Using the test script:
```bash
python test_api.py
# Follow the prompts to upload a PDF
```

### Using Python:
```python
from example_usage import SecondBrainClient

client = SecondBrainClient()
result = client.upload_pdf("my_document.pdf")
print(f"Uploaded: {result['title']}")
```

## Step 6: Search Your Documents

### Using curl:
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "top_k": 5}'
```

### Using Python:
```python
results = client.search("machine learning", top_k=5)
for result in results['results']:
    print(f"{result['document_title']}: {result['content'][:100]}...")
```

## Common Commands

```bash
# Start server
python -m app.main

# Run tests
python test_api.py

# Format code
black app/

# Check health
curl http://localhost:8000/api/health
```

## Troubleshooting

### "ModuleNotFoundError"
- Make sure virtual environment is activated: `source venv/bin/activate`

### "OpenAI API Error"
- Check your API key in `.env` file
- Verify key has credits: https://platform.openai.com/account/usage

### "Connection refused"
- Make sure server is running: `python -m app.main`
- Check port 8000 is not in use

### "PDF Processing Error"
- Verify PDF is not encrypted
- Check file is valid PDF format
- Ensure file size is under 50MB

## Next Steps

1. Upload multiple PDFs to build your knowledge base
2. Experiment with different search queries
3. Explore the API documentation: http://localhost:8000/docs
4. Check out [example_usage.py](example_usage.py) for integration examples

## Getting Help

- Read the full [README.md](README.md)
- Check API docs: http://localhost:8000/docs
- Review the code in `app/` directory

Happy searching! 🧠✨
