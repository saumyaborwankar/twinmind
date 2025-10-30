# Phase 2 Quick Start: RAG & Q&A

## Setup (2 minutes)

### 1. Update Configuration

```bash
# Edit your .env file
nano .env

# Add these lines:
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1500
```

### 2. Restart Server

```bash
# Stop the server (Ctrl+C if running)
# Start it again
python -m app.main
```

You should see:
```
INFO: Application startup complete
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 3. Test It

```bash
# In a new terminal
python test_rag.py
```

That's it! Your RAG system is ready.

---

## Your First Question

### Using the Test Script

```bash
python test_rag.py
# Follow the prompts to ask questions
```

### Using curl

```bash
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main topics in my documents?",
    "top_k": 5
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/rag/ask",
    json={"question": "What are the key findings?"}
)

data = response.json()
print(f"Answer: {data['answer']}\n")
print(f"Sources: {len(data['sources'])}")
```

### Using the API Docs

Visit http://localhost:8000/docs and try the `/api/rag/ask` endpoint

---

## Common Questions

### Q: Do I need to re-upload my PDFs?
**A:** No! Your existing documents work automatically with RAG.

### Q: What models can I use?
**A:**
- `gpt-4-turbo-preview` (recommended, $$$)
- `gpt-4` (highest quality, $$$$)
- `gpt-3.5-turbo` (fast & cheap, $)
- `gpt-3.5-turbo-16k` (longer context, $$)

### Q: How much does it cost?
**A:** About $0.04 per question with GPT-4 Turbo. Use GPT-3.5 to save 90%.

### Q: Can I ask follow-up questions?
**A:** Yes! Use the `/api/rag/conversation` endpoint with conversation history.

### Q: Are answers always accurate?
**A:** Check the confidence score and verify sources. Low confidence = verify carefully.

---

## Quick Examples

### Simple Q&A
```bash
# Ask about your documents
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize the main points"}'
```

### With Streaming
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/rag/ask/stream",
    json={"question": "Explain the methodology"},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8')[6:])
        if data['type'] == 'answer':
            print(data['data'], end='', flush=True)
```

### Summarize a Document
```bash
# Get document ID first
DOC_ID=$(curl -s "http://localhost:8000/api/documents" | jq -r '.documents[0].id')

# Summarize it
curl -X POST "http://localhost:8000/api/rag/summarize" \
  -H "Content-Type: application/json" \
  -d "{\"document_id\": \"$DOC_ID\"}"
```

---

## Troubleshooting

### Error: "OpenAI API key not found"
```bash
# Check your .env file
cat .env | grep OPENAI_API_KEY

# Make sure it's set correctly
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### Error: "No relevant documents found"
- Upload more PDFs: `python test_api.py`
- Try different question phrasing
- Check if documents have content

### Slow responses
- Use `gpt-3.5-turbo` instead of `gpt-4`
- Reduce `top_k` to retrieve fewer chunks
- Lower `max_tokens` for shorter answers

### High costs
- Switch to `gpt-3.5-turbo` (much cheaper)
- Reduce `top_k` (less context)
- Lower `max_tokens` (shorter answers)

---

## Next Steps

1. **Upload Documents**: Add more PDFs to improve answers
2. **Try Questions**: Test different types of questions
3. **Adjust Settings**: Experiment with temperature and top_k
4. **Read Docs**: See [PHASE2_RAG.md](PHASE2_RAG.md) for details

---

## Quick Reference

```bash
# Configuration
LLM_MODEL=gpt-4-turbo-preview  # or gpt-3.5-turbo for cheaper
LLM_TEMPERATURE=0.7             # 0.0-1.0 (lower = more focused)
LLM_MAX_TOKENS=1500            # max response length

# Start server
python -m app.main

# Test RAG
python test_rag.py

# API docs
open http://localhost:8000/docs

# Simple question
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "your question"}'
```

---

**That's it! Start asking questions about your documents! 🚀**

For more details: [PHASE2_RAG.md](PHASE2_RAG.md)
