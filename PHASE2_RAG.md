# Phase 2: RAG & Q&A System

## Overview

Phase 2 adds **Retrieval-Augmented Generation (RAG)** capabilities to your Second Brain, transforming it from a document search engine into an intelligent Q&A system that can understand and answer questions about your documents using natural language.

## New Features

### 1. **Question Answering (RAG)**
Ask natural language questions and get intelligent answers based on your documents:
- Retrieves relevant context from your knowledge base
- Uses GPT-4 to generate comprehensive answers
- Provides source citations for transparency
- Confidence scoring for answer quality

### 2. **Streaming Responses**
Get answers in real-time as they're generated:
- Better UX for longer responses
- Lower perceived latency
- Source citations provided upfront

### 3. **Conversation History**
Maintain context across multiple questions:
- Follow-up questions work naturally
- References previous answers
- Multi-turn dialogue support

### 4. **Document Summarization**
Generate concise summaries of entire documents:
- Automatic analysis of document content
- Key points extraction
- Configurable summary length

## Architecture

```
[User Question]
      ↓
[Semantic Search] → Retrieve Top K relevant chunks
      ↓
[Context Builder] → Format chunks with metadata
      ↓
[LLM (GPT-4)] → Generate answer with sources
      ↓
[Response] → Answer + Citations + Confidence
```

## API Endpoints

### POST /api/rag/ask
Ask a question and get an answer with sources.

**Request:**
```json
{
  "question": "What are the main findings about climate change?",
  "top_k": 5,
  "include_sources": true,
  "system_prompt": "optional custom instructions"
}
```

**Response:**
```json
{
  "answer": "Based on your documents, the main findings are...",
  "sources": [
    {
      "source_id": 1,
      "document_title": "Climate Report 2024.pdf",
      "page_number": 5,
      "relevance_score": 0.89,
      "content_preview": "Global temperatures have..."
    }
  ],
  "context_used": 5,
  "confidence": "high",
  "model": "gpt-4-turbo-preview",
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 567,
    "total_tokens": 1801
  }
}
```

### POST /api/rag/ask/stream
Ask a question with streaming response.

**Request:** Same as `/api/rag/ask`

**Response:** Server-Sent Events (SSE) stream:
```
data: {"type":"sources","data":[...]}

data: {"type":"answer","data":"Based on"}
data: {"type":"answer","data":" your documents"}
data: {"type":"answer","data":"..."}

data: {"type":"done"}
```

### POST /api/rag/conversation
Ask questions with conversation history.

**Request:**
```json
{
  "question": "What about the methodology?",
  "conversation_history": [
    {"role": "user", "content": "What are the findings?"},
    {"role": "assistant", "content": "The main findings are..."}
  ],
  "top_k": 5
}
```

**Response:** Same as `/api/rag/ask`

### POST /api/rag/summarize
Summarize a specific document.

**Request:**
```json
{
  "document_id": "abc-123-def-456"
}
```

**Response:**
```json
{
  "document_id": "abc-123-def-456",
  "document_title": "Research Paper.pdf",
  "summary": "This paper discusses...",
  "page_count": 25,
  "chunks_analyzed": 20
}
```

## Configuration

New environment variables in `.env`:

```bash
# LLM Settings for RAG
LLM_MODEL=gpt-4-turbo-preview       # Model to use (gpt-4, gpt-3.5-turbo, etc.)
LLM_TEMPERATURE=0.7                  # Creativity (0.0-1.0)
LLM_MAX_TOKENS=1500                  # Max response length
```

### Model Options

| Model | Cost | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| gpt-4-turbo-preview | $$$ | Medium | Excellent | Complex questions, synthesis |
| gpt-4 | $$$$ | Slow | Excellent | Critical answers, research |
| gpt-3.5-turbo | $ | Fast | Good | Simple Q&A, quick lookups |
| gpt-3.5-turbo-16k | $$ | Fast | Good | Long context questions |

**Recommendation:** `gpt-4-turbo-preview` for best balance

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Simple question
response = requests.post(
    f"{BASE_URL}/api/rag/ask",
    json={
        "question": "What are the key recommendations?",
        "top_k": 5
    }
)

data = response.json()
print(f"Answer: {data['answer']}\n")
print(f"Sources: {len(data['sources'])}")
for source in data['sources']:
    print(f"  - {source['document_title']}, p.{source['page_number']}")
```

### Conversation

```python
history = []

# First question
q1 = "What is the main topic?"
r1 = requests.post(f"{BASE_URL}/api/rag/conversation", json={
    "question": q1,
    "conversation_history": history
}).json()

print(r1['answer'])

# Add to history
history.append({"role": "user", "content": q1})
history.append({"role": "assistant", "content": r1['answer']})

# Follow-up question
q2 = "Can you elaborate on that?"
r2 = requests.post(f"{BASE_URL}/api/rag/conversation", json={
    "question": q2,
    "conversation_history": history
}).json()

print(r2['answer'])
```

### Streaming

```python
import json

response = requests.post(
    f"{BASE_URL}/api/rag/ask/stream",
    json={"question": "Explain the methodology in detail"},
    stream=True
)

for line in response.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data = json.loads(line_str[6:])

            if data['type'] == 'sources':
                print(f"Sources: {len(data['data'])}")

            elif data['type'] == 'answer':
                print(data['data'], end='', flush=True)

            elif data['type'] == 'done':
                print("\n\nDone!")
```

### curl

```bash
# Simple question
curl -X POST "http://localhost:8000/api/rag/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "top_k": 5
  }'

# Summarize document
curl -X POST "http://localhost:8000/api/rag/summarize" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "abc-123"}'
```

## Testing

Run the test suite:

```bash
python test_rag.py
```

This will test:
1. ✅ Simple Q&A
2. ✅ Streaming responses
3. ✅ Conversation with history
4. ✅ Document summarization

## How It Works

### 1. Question Processing
```python
question = "What are the main findings?"
# System analyzes intent and extracts key terms
```

### 2. Context Retrieval
```python
# Semantic search finds relevant chunks
chunks = search_service.semantic_search(query=question, top_k=5)
# Returns: [chunk1, chunk2, chunk3, chunk4, chunk5]
```

### 3. Context Formatting
```python
context = """
[Source 1: Report.pdf, Page 5, Relevance: 0.89]
The study found that global temperatures...

[Source 2: Analysis.pdf, Page 12, Relevance: 0.85]
Key findings include a 13% decrease...
"""
```

### 4. LLM Generation
```python
# Send to GPT-4 with system prompt
system_prompt = "Answer based only on provided context..."
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
]
answer = llm.generate(messages)
```

### 5. Response Formatting
```python
response = {
    "answer": answer,
    "sources": extract_sources(chunks),
    "confidence": calculate_confidence(chunks),
    "usage": token_usage
}
```

## Advanced Features

### Custom System Prompts

Control the AI's behavior:

```python
custom_prompt = """
You are a medical research assistant.
Analyze the provided context with focus on:
- Statistical significance
- Methodology rigor
- Clinical implications
Be extremely precise with numbers and citations.
"""

response = requests.post(f"{BASE_URL}/api/rag/ask", json={
    "question": "What were the trial results?",
    "system_prompt": custom_prompt
})
```

### Confidence Scoring

Answers include confidence levels:
- **high** (>0.8): Very relevant sources found
- **medium** (0.6-0.8): Relevant sources found
- **low** (<0.6): Marginal relevance
- **none**: No relevant sources

Use confidence to decide whether to trust the answer or search for more information.

### Source Citations

Every answer includes source tracking:
- Document title
- Page number
- Relevance score
- Content preview
- Direct link to source chunk

## Cost Analysis

### OpenAI API Costs (GPT-4 Turbo)

- **Input**: $0.01 per 1K tokens
- **Output**: $0.03 per 1K tokens

**Typical Q&A:**
- Context: ~2,500 tokens (5 chunks × 500 tokens)
- Question: ~50 tokens
- Answer: ~500 tokens
- **Cost per question**: ~$0.04

**Monthly estimates:**
- 100 questions/day: ~$120/month
- 50 questions/day: ~$60/month
- 10 questions/day: ~$12/month

### Cost Optimization Tips

1. **Use GPT-3.5-Turbo** for simple questions (~90% cheaper)
2. **Reduce `top_k`** to retrieve fewer chunks
3. **Limit `max_tokens`** to shorter answers
4. **Cache common questions** (future feature)

## Best Practices

### 1. Ask Good Questions

❌ Bad: "climate"
✅ Good: "What are the main findings about climate change impacts?"

❌ Bad: "numbers"
✅ Good: "What are the key statistical findings?"

### 2. Use Appropriate top_k

- **Simple questions**: top_k=3
- **Complex questions**: top_k=5-7
- **Comprehensive analysis**: top_k=10

### 3. Check Confidence

```python
if response['confidence'] in ['low', 'none']:
    print("⚠️ Low confidence - answer may be unreliable")
    # Consider rephrasing question or adding more documents
```

### 4. Verify Sources

Always check the cited sources to verify accuracy:

```python
for source in response['sources']:
    print(f"📄 {source['document_title']}, p.{source['page_number']}")
    print(f"   Relevance: {source['relevance_score']:.2f}")
    # Read the actual page if accuracy is critical
```

## Troubleshooting

### Issue: Low-quality answers

**Solutions:**
- Upload more relevant documents
- Use more specific questions
- Increase `top_k` for more context
- Try different `system_prompt`

### Issue: "No relevant documents found"

**Solutions:**
- Check if documents are uploaded
- Try different query phrasing
- Check document content quality
- Verify embeddings were generated

### Issue: Answers cite wrong sources

**Solutions:**
- Check source relevance scores
- Increase `top_k` to get better context
- Improve document chunking (adjust CHUNK_SIZE)
- Add more diverse documents

### Issue: High API costs

**Solutions:**
- Switch to gpt-3.5-turbo
- Reduce `max_tokens`
- Decrease `top_k`
- Batch similar questions

## What's Next?

Future enhancements (Phase 3):
- **Hybrid search**: Combine semantic + keyword search
- **Re-ranking**: Cross-encoder for better results
- **Query expansion**: Automatic synonym/related terms
- **Multi-query**: Generate multiple search queries
- **Answer caching**: Cache common questions
- **Custom extractors**: Extract specific data types
- **Evaluation metrics**: Track answer quality
- **A/B testing**: Compare different prompts/models

## Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

---

**Your Second Brain now has conversational intelligence! 🧠✨**

Start asking questions:
```bash
python test_rag.py
```
