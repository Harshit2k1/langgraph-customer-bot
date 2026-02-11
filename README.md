# Customer Support LangGraph Multi‑Agent AI System

An AI-powered customer support assistant that combines **LangGraph orchestration**, **RAG over policy PDFs**, and **SQL customer data** to answer questions through a Streamlit UI.

## ✨ Features

- **Natural language SQL queries** for customer profiles and support ticket data
- Multi-agent orchestration with **LangGraph** (router decides: SQL, RAG, or both)
- **RAG pipelin**e with **LanceDB** vector store for persistent policy knowledge
- **Local embedding model** (sentence-transformers/all-mpnet-base-v2) for document vectorization
- Context-aware responses combining **structured** and **unstructured data**
- **MCP Server** for AI assistant integration
- **Streamlit UI** with chat interface, document upload manager, and system statistics
- **Temporary session documents** for quick uploads without saving
- Synthetic customer data (profiles, support tickets) with generation scripts

## 🧱 Project structure

```
app.py                         # Streamlit UI
src/
	agents/                      # RAG + SQL agents
	database/                    # SQL + vector DB helpers
	orchestration/               # LangGraph setup
	processing/                  # PDF chunking + ingestion
	utils/                       # Session handling
scripts/                       # Data generation + setup scripts
data/                          # Sample PDFs + database assets
vectorstore/                   # LanceDB storage
```

## ✅ Prerequisites

- Python 3.10+ (3.11 recommended)
- An OpenAI API key

## ⚙️ Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file in the repo root:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-gpt-5-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

> The deafult config keys are loaded in `src/config.py`. Adjust the values above if your config differs.

## ▶️ Run the app

```bash
streamlit run app.py
```

## 🧪 Generate sample data (optional)

For structured Data:
```bash
python scripts/setup_db.py
python scripts/generate_data.py
```

For unstructured Data:
```bash
python scripts/generate_policies.py
```

## 📄 Uploading documents

- Use the sidebar **Upload PDF** control.
- Toggle **Save Permanently** to persist in LanceDB.
- Temporary uploads are used for the current session only.

## 🔐 Environment configuration

Settings are read from `src/config.py` (via environment variables). Common keys:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `EMBEDDING_MODEL`

## 📌 Notes

- This project uses **LangGraph**, **LanceDB**, **MCP Server** and **Streamlit**.
- SQLite data lives under `data/database/`.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
