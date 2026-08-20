# Self-Hosted PostgreSQL Natural Language SQL Agent

A fully self-hosted Natural Language → PostgreSQL SQL agent powered by local CPU LLM inference (`Qwen2.5-Coder-7B-Instruct-GGUF`), `llama.cpp` (`llama-server`), `LangGraph`, `FastAPI`, and robust AST SQL security validation.

---

## 🌟 Key Features

- **100% Self-Hosted & Local**: No external LLM APIs (No OpenAI, Anthropic, or cloud API dependencies).
- **CPU Optimized**: Runs `Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M` locally via `llama-server` on standard CPU hardware (12-16 GB RAM).
- **ClickHouse / PostgreSQL Compatible**: Built to query ClickHouse data lake (`epdatalake` schema) via PostgreSQL wire protocol (`psycopg`).
- **8-Layer Security Boundary**:
  1. Input validation & category classification
  2. AST SQL parsing (`sqlglot`) & single-statement enforcement
  3. Strict SELECT/CTE only query rules
  4. Table allowlist (`ALLOWED_TABLES`) & column allowlists
  5. Sensitive column blocking (`password`, `token`, `credentials`, etc.)
  6. EXPLAIN cost evaluation (`MAX_QUERY_COST=10000.0`)
  7. Dedicated read-only database user with SELECT-only permissions
  8. Configurable statement timeout (`SQL_STATEMENT_TIMEOUT_MS=5000`) and read-only transactions.
- **LangGraph Agent Workflow**: Explicit node architecture (`classify_question` → `discover_schema` → `retrieve_schema` → `generate_sql` → `validate_sql` → `execute_sql` / `repair_sql` → `generate_answer`).
- **Semantic Catalog & Retrieval**: Concise schema retriever dynamically selecting relevant schemas and explicit table relationships to prevent context bloat.
- **Audit Logging**: Full lifecycle request tracking including request ID, question, tables, generated SQL, execution latency, row counts, and status.

---

## 🚀 Quick Start

### 1. Prerequisites
- Linux OS (Ubuntu 22.04+ / Debian)
- Python 3.11+
- PostgreSQL 14+
- `llama-server` (compiled or downloaded)

### 2. Environment Setup & Dependencies
```bash
git clone https://github.com/your-org/sql_agent.git
cd sql_agent
python3 -m pip install -r requirements.txt
cp .env.example .env  # or configure .env directly
```

### 3. Database Setup
```bash
# Setup database, seed data, read-only user, and analytical views
sudo -u postgres psql -c "CREATE DATABASE electricity;"
sudo -u postgres psql -d electricity -f scripts/setup_database.sql
sudo -u postgres psql -d electricity -f database/permissions.sql
sudo -u postgres psql -d electricity -f database/views.sql
```

### 4. Start Local LLM Server
```bash
./scripts/start_llm.sh
```
The server will run at `http://127.0.0.1:8080/v1`.

### 5. Start Backend Server
```bash
./scripts/start_backend.sh
```
FastAPI server starts at `http://127.0.0.1:8000`.

---

## 🧪 Testing & Verification

Run the test suite:
```bash
pytest
```

Includes tests for:
- AST SQL parsing and validator rules (`tests/test_sql_validator.py`)
- Security & adversarial query rejection (`tests/test_security.py`)
- Schema retriever precision (`tests/test_schema_retrieval.py`)
- End-to-end question processing benchmark (`tests/test_agent.py`)

---

## 📡 API Reference

### POST `/api/query`
Processes natural language questions.

#### Request Body
```json
{
  "question": "What was the average consumption yesterday?",
  "include_sql": true
}
```

#### Response Body
```json
{
  "answer": "The average consumption yesterday was 143.20 kWh.",
  "sql": "SELECT AVG(consumption) AS avg_consumption FROM consumption WHERE timestamp >= CURRENT_DATE - INTERVAL '1 day' AND timestamp < CURRENT_DATE;",
  "execution_time_ms": 142.5,
  "status": "success",
  "tables_used": ["consumption"],
  "audit_id": "8a39178f-6242-4f32-a50d-83b6f00ab9c2"
}
```

### Health Check Endpoints
- `GET /health` - FastAPI service status
- `GET /health/llm` - llama-server connectivity
- `GET /health/database` - PostgreSQL connectivity
