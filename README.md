# 🤖 AI Micro-Agent: Technical Article Analyzer

> A lightweight AI agent that fetches a technical article, summarizes it into **3 concise bullet points**, extracts key technologies, saves structured JSON output, and triggers a webhook — with robust edge-case handling and smart performance optimization.

---

## 📁 Project Structure

```
AI-AGENT-TASK/
├── agent/
│   ├── fetcher.py          # URL fetching & HTML parsing
│   ├── processor.py        # Text cleaning, validation, chunking
│   └── extractor.py        # AI summarization & tech extraction
├── utils/
│   ├── json_handler.py     # Output formatting, deduplication, confidence scoring
│   └── webhook.py          # Mock/real webhook dispatcher
├── .env                    # API keys (not committed)
├── main.py                 # Pipeline orchestrator
├── output.json             # Final structured result
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd AI-AGENT-TASK

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Add your OpenAI API key inside .env:
# OPENAI_API_KEY=sk-...
```

---

## 🚀 How to Run

```bash
python main.py
```

To test with a custom URL, edit `main.py`:

```python
test_url = "https://your-article-url-here.com"
run_pipeline(test_url)
```

---

## 🏗️ Architecture

```
User Input (URL)
       ↓
[fetcher.py]  →  Fetch & parse HTML content (BeautifulSoup)
       ↓
[processor.py] → Clean text + validate length + chunk with overlap
       ↓
[extractor.py] → AI processes 3 representative chunks (GPT-4.1-mini)
       ↓           ├── Summarize each chunk
       ↓           └── Extract technologies per chunk
       ↓
[extractor.py] → Aggregate: combine + deduplicate + final AI refinement
       ↓
[json_handler.py] → Format output + confidence scoring + metadata
       ↓
[webhook.py]  →  Send to webhook URL or print to console
       ↓
[output.json] →  Persist structured result to disk
```

---

## 🛠️ Tech Stack & Tool Choices

| Tool | Purpose | Why |
|------|---------|-----|
| `requests` | HTTP fetching | Lightweight, reliable, supports timeout config |
| `BeautifulSoup` | HTML parsing | Strips scripts/styles, extracts visible text cleanly |
| `OpenAI GPT-4.1-mini` | Summarization + extraction | Fast, cost-efficient, strong JSON instruction following |
| `python-dotenv` | Env variable management | Keeps secrets out of source code |
| `json` (stdlib) | Output persistence | No extra dependency needed for structured output |

---

## ⚡ Performance Optimization

### The Problem
The initial naive approach processed **every chunk** of a long article separately:
- ~16 chunks per article
- 2 API calls per chunk (summary + extraction)
- **~32 API calls per request → ~60 seconds latency**

### The Solution: Representative Chunk Sampling

Instead of processing all chunks, the agent now selects **3 strategically positioned chunks**:

```
Full article
    ├── Chunk[0]         → Introduction / context
    ├── Chunk[n//2]      → Core content / body
    └── Chunk[-2]        → Conclusion (avoiding nav/footer noise at [-1])
```

**Why `chunks[-2]` instead of `chunks[-1]`?**
The last chunk often contains footer noise, navigation links, and unrelated content. The second-to-last chunk reliably captures the article's conclusion.

### Results

| Stage | API Calls | Latency |
|-------|-----------|---------|
| Full chunks (naive) | ~32 calls | ~60s ❌ |
| 3 smart chunks | ~4 calls | <10s ✅ |

**Reduction: 80–90% fewer API calls, 6x faster.**

The approach mirrors **map-reduce**: summarize in parallel per chunk, then aggregate into a final coherent output.

---

## 🧠 AI Processing Strategy

### Two-Stage Summarization

**Stage 1 — Per-chunk processing** (`process_chunk_with_ai`):
Each representative chunk is sent to the LLM with a strict prompt:
- Produce exactly 3 bullet points
- Extract all mentioned technologies
- Return **only valid JSON** — no prose, no markdown fences

**Stage 2 — Aggregation** (`aggregate_results`):
All chunk outputs are merged and sent to a final refinement call:
- Deduplicates and merges redundant summaries
- Produces the definitive 3-bullet summary
- Cleans and normalizes the technology list

### Prompt Engineering Decisions
- **Role assignment**: `"You are an expert AI technical analyst"` improves output quality
- **Strict JSON constraint**: System prompt enforces `"Always return valid JSON only"` to prevent markdown wrapping
- **Low temperature (0.2)**: Reduces hallucinations, improves consistency
- **Fallback parsing**: If JSON parsing fails, the agent gracefully falls back to partial results rather than crashing

---

## ✨ Key Enhancements

### 1. Technology Deduplication
Raw LLM output often returns the same technology with slight variations across chunks (e.g., `"OpenAI"`, `"openai"`, `"Open AI"`). The deduplication logic normalizes entries before comparison:

```python
normalized = tech.strip().lower().replace("-", " ").replace("_", " ")
```

This preserves the original casing in output while eliminating duplicates — order is also preserved (first occurrence wins).

### 2. Confidence Scoring
A heuristic score (0.0–0.95) is computed to indicate output reliability:

| Factor | Contribution |
|--------|-------------|
| Base score | +0.50 |
| Each valid summary point (≥5 words) | +0.08 (max +0.24) |
| Each meaningful technology | +0.025 (max +0.21) |

This gives evaluators a transparent signal of extraction quality without requiring ground truth labels.

### 3. Metadata Tracking
Every output includes operational metadata:
```json
"metadata": {
    "processing_time": 7.43,
    "chunks_used": 3
}
```
This enables performance monitoring and demonstrates system observability.

---

## ⚠️ Edge Cases & Handling

| Scenario | Handling |
|----------|---------|
| ❌ Invalid / malformed URL | `requests.exceptions.RequestException` caught, status = `"failed: Invalid URL or connection error."` |
| ⏳ Request timeout | `timeout=10` on all requests; `Timeout` exception caught separately with a clear message |
| 📭 Empty page / no content | Content length validated (`< 200 chars` → raises exception before any AI calls) |
| 🔒 Paywalled content | Non-200 status codes are caught and reported; short content check catches soft paywalls |
| 📚 Extremely long articles | Chunking with `max_length=2000, overlap=100` then smart 3-chunk sampling keeps token usage bounded |
| 🧠 Non-technical articles | Agent still produces output gracefully; technologies list may be short, confidence score will reflect this |
| 💥 LLM returns malformed JSON | `try/except` around `json.loads`; fallback returns partial results rather than crashing |
| 🌐 Webhook endpoint unavailable | Timeout and connection errors handled; falls back to console print if no URL provided |

---

## 📊 Example Output

```json
{
    "url": "https://www.ibm.com/think/topics/artificial-intelligence",
    "summary": [
        "Artificial Intelligence enables machines to simulate human cognitive functions such as learning, reasoning, and problem-solving across diverse domains.",
        "Modern AI systems rely on machine learning and deep learning techniques to train models on large datasets, enabling pattern recognition and predictive capabilities.",
        "AI is being adopted across industries including healthcare, finance, and manufacturing to automate processes, enhance decision-making, and drive innovation."
    ],
    "technologies": [
        "Artificial Intelligence",
        "Machine Learning",
        "Deep Learning",
        "Natural Language Processing",
        "Neural Networks",
        "Python",
        "TensorFlow"
    ],
    "status": "success",
    "metadata": {
        "processing_time": 7.43,
        "chunks_used": 3
    },
    "confidence": 0.87
}
```

---

## 🧪 Testing Scenarios

| Scenario | Input | Expected Result |
|----------|-------|----------------|
| ✅ Valid technical article | `https://ibm.com/think/topics/...` | Full summary + technologies, `status: success` |
| ❌ Invalid URL | `"not-a-url"` | `status: "failed: Invalid URL or connection error."` |
| ⏳ Slow server | URL with 15s+ response | `status: "failed: Request timed out."` |
| 📭 Empty page | URL returning blank HTML | `status: "failed: Article content is too short or empty."` |
| 📚 Long article | 50,000+ character page | Chunked → 3 representative chunks → processed in <10s |
| 🧠 Non-technical blog | Lifestyle article URL | Output produced gracefully, low confidence score |

---

## 🔐 Environment Variables

```env
OPENAI_API_KEY=sk-your-key-here
```

Never commit `.env` to version control. A `.env.example` file is provided as a template.

---

## 📦 Dependencies

```
requests
beautifulsoup4
openai
python-dotenv
```

Install with:
```bash
pip install -r requirements.txt
```

This solution is designed to balance accuracy, cost efficiency, and scalability, making it suitable for real-world AI agent pipelines.

## 👤 About the Author

**Abdulrahman Salah**  
AI Engineer |

Passionate about designing and building intelligent systems that combine LLMs, automation, and scalable backend architecture.

🔗 LinkedIn: https://www.linkedin.com/in/abdulrahman--salah/  
📧 Email: abdulrahmansalah107@gmail.com
