# FlowReign AI
### Intelligence That Executes.

<p align="center">
  <strong>An Open-Source Business Operations Intelligence Platform</strong>
</p>

<p align="center">
  <a href="https://github.com/Manikanta-23-ai/flowreign-ai">GitHub Repository</a> ·
  <a href="https://manikanta-23-ai.github.io/flowreign-ai/">Project Website</a> ·
  <a href="https://github.com/Manikanta-23-ai/flowreign-ai/issues">Report an Issue</a>
</p>

---

## Overview

**FlowReign AI** is an open-source business operations intelligence platform designed to bring workflow orchestration, data intelligence, evidence collection, AI-assisted analysis, and human-in-the-loop execution into one extensible system.

The project explores how AI-assisted specialist agents and deterministic workflow engines can work together to simplify operational processes.

Instead of treating AI as just a chatbot, FlowReign AI focuses on structured execution:

- Break operational objectives into actionable tasks.
- Organize tasks using dependencies.
- Analyze structured datasets.
- Collect evidence from user-provided URLs.
- Explore specialist AI-assisted analysis.
- Require human approval at designated execution checkpoints.
- Generate structured operational reports.

The long-term vision is to develop an extensible operations intelligence system that connects AI reasoning with practical business workflows.

## Core Features

### 1. Workflow Intelligence

A workflow engine for creating and managing operational workflows.

- Create and manage workflows.
- Generate structured task plans.
- Organize task dependencies.
- Track workflow execution.
- Persist workflow information using SQLite.
- Support human approval checkpoints.

### 2. Data Intelligence

Analyze CSV datasets using Python and Pandas.

Capabilities include:

- Dataset previews.
- Row and column information.
- Numeric and categorical summaries.
- Missing-value analysis.
- Duplicate detection.
- Numeric correlations.
- Structured analysis results.
- Data visualization through Streamlit.

### 3. Evidence Research Agent

A research component that collects information from user-provided URLs.

Capabilities include:

- HTTP/HTTPS source retrieval.
- HTML and plain-text extraction.
- Objective-based sentence relevance scoring.
- Source URL tracking.
- Retrieval timestamps.
- Structured evidence output.

**Important:** This is URL-based evidence collection, not an autonomous internet search engine. Retrieved snippets are not independently verified.

### 4. Specialist AI Agents

An AI-assisted specialist framework designed around different operational responsibilities.

Specialist roles include:

- Planning Agent
- Research Agent
- Analysis Agent
- Data Analyst
- Automation Analyst
- Report Generation Agent
- Quality Assurance Agent

The specialist framework uses model-assisted analysis where configured.

### 5. Unified Operations

A unified API endpoint combines selected operational capabilities into one request.

The current implementation coordinates research and CSV analysis through deterministic service orchestration.

### 6. Human-in-the-Loop Execution

FlowReign AI incorporates human approval into its workflow execution design.

The goal is to keep consequential operations reviewable instead of allowing unrestricted autonomous execution.

### 7. Operational Reports

Generate structured workflow reports.

Supported report formats:

- JSON
- CSV

---

## Architecture

FlowReign AI follows a modular architecture separating API endpoints, business logic, workflow execution, AI components, and the user interface.

```text
                 FLOWREIGN AI
                       |
          +------------+------------+
          |                         |
      Streamlit UI              FastAPI
          |                         |
          |              +----------+----------+
          |              |          |          |
          |          Workflows    Data      Research
          |              |          |          |
          |              +----------+----------+
          |                         |
          |                  Service Layer
          |                         |
          |              +----------+----------+
          |              |          |          |
          |           Planner    Executor   Reports
          |              |          |          |
          |              +----------+----------+
          |                         |
          |                  AI Components
          |                         |
          |               Specialist Agents
          |                         |
          +-------------------------+
                                    |
                                SQLite DB
```

### Project Structure

```text
flowreign-ai/
│
├── backend/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── workflows.py
│   │   ├── data.py
│   │   ├── reports.py
│   │   ├── research.py
│   │   └── operations.py
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── schemas/
│   │   ├── workflow.py
│   │   ├── data.py
│   │   ├── research.py
│   │   └── operations.py
│   │
│   └── services/
│       ├── workflow_service.py
│       ├── data_service.py
│       ├── report_service.py
│       ├── research_service.py
│       └── operations_service.py
│
├── core/
│   ├── engine/
│   │   ├── planner.py
│   │   └── executor.py
│   │
│   ├── ai/
│   │   └── provider.py
│   │
│   └── agents/
│       └── specialists.py
│
├── frontend/
│   ├── app.py
│   └── pages/
│       └── 2_Data_Intelligence.py
│
├── tests/
│   └── test_workflows.py
│
├── docs/
│   └── index.html
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming language | Python |
| Backend framework | FastAPI |
| Frontend dashboard | Streamlit |
| Data analysis | Pandas |
| Database | SQLite |
| Data validation | Pydantic |
| AI integration | Google Gemini provider |
| API communication | REST APIs |
| Testing | Pytest, HTTPX |
| Version control | Git, GitHub |
| CI/CD | GitHub Actions |
| Deployment documentation | GitHub Pages |

---

## Installation and Setup

### Prerequisites

- Python 3.12 or later.
- Git.
- Internet connection for dependency installation.
- A Gemini API key if using the configured Gemini functionality.

### 1. Clone the Repository

```bash
git clone https://github.com/Manikanta-23-ai/flowreign-ai.git
```

```bash
cd flowreign-ai
```

### 2. Create a Virtual Environment

Windows:

```cmd
py -m venv .venv
```

Activate it:

```cmd
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create your local environment file:

```cmd
copy .env.example .env
```

Configure the provider settings required by `core/ai/provider.py`.

Add your own Gemini API key using the exact variable name expected by the provider implementation.

**Security:** Never commit `.env` or expose API keys in source code, screenshots, URLs, or public repositories.

### 5. Start the FastAPI Backend

```bash
uvicorn backend.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the Streamlit Dashboard

Open another terminal:

```bash
streamlit run frontend/app.py
```

Dashboard:

`http://localhost:8501`

---

## API Capabilities

The backend exposes versioned API routes.

| Endpoint | Purpose |
|---|---|
| `/api/v1/workflows` | Workflow management |
| `/api/v1/data` | Dataset intelligence |
| `/api/v1/reports/{workflow_id}/json` | JSON workflow report |
| `/api/v1/reports/{workflow_id}/csv` | CSV workflow report |
| `/api/v1/research` | Evidence research |
| `/api/v1/operations/run` | Unified operations |

For exact request schemas, parameters, and response structures, use the interactive Swagger documentation:

`http://127.0.0.1:8000/docs`

---

## Example Use Cases

### Business Operations

Organize a business objective into structured tasks and manage the execution process.

### Dataset Intelligence

Upload a CSV file, inspect its structure, identify missing values, analyze numeric columns, and explore correlations.

### Evidence Collection

Provide relevant URLs and an objective to collect and organize supporting information.

### Operational Reporting

Generate structured reports from workflow records for further inspection and analysis.

### AI-Assisted Analysis

Use configured specialist components to explore planning, research, analysis, and reporting tasks.

---

## Testing

Run the test suite:

```bash
python -m pytest -q
```

Run the workflow tests separately:

```bash
python -m pytest tests/test_workflows.py -q
```

The workflow test suite previously passed five tests in the local development environment. Run the complete test suite against your current checkout before treating the entire application as validated.

### Continuous Integration

GitHub Actions is configured to automate testing when changes are pushed to the `main` branch or submitted through pull requests.

Workflow configuration:

```text
.github/workflows/tests.yml
```

View workflow results:

https://github.com/Manikanta-23-ai/flowreign-ai/actions

---

## Security Considerations

FlowReign AI is an evolving development project. Security hardening is ongoing.

Current design considerations include:

- Environment-based configuration for secrets.
- SQLite-based local persistence.
- Human approval checkpoints.
- HTTP/HTTPS URL validation in evidence collection.
- Restrictions on private IP addresses and custom ports in URL retrieval.
- Limited response size and blocked redirects in the research component.

This implementation should not be considered production-grade security. Additional work is needed for comprehensive SSRF protection, authentication, authorization, rate limiting, audit logging, and deployment hardening.

---

## Current Limitations

Transparency matters. The current MVP has deliberate limitations:

1. **Planning:** Workflow planning is currently deterministic and rule-based, not a fully autonomous AI planning system.
2. **Research:** The research component retrieves user-supplied URLs; it does not perform general web search.
3. **Evidence:** Extracted evidence snippets are not independently fact-checked.
4. **Operations:** Unified operations currently uses deterministic service orchestration.
5. **AI agents:** Specialist agent functionality depends on the configured model provider and is not equivalent to a fully autonomous multi-agent production system.
6. **Persistence:** SQLite is currently used for local workflow persistence.
7. **Deployment:** GitHub Pages hosts the static project website, not the FastAPI backend or Streamlit dashboard.

---

## Roadmap

The following items are planned areas of development, not claims of completed functionality.

### Phase 1 — Core Platform

- [x] FastAPI backend foundation
- [x] Workflow management
- [x] Deterministic workflow planner
- [x] Workflow execution foundation
- [x] SQLite persistence
- [x] Human approval checkpoints
- [x] CSV data intelligence
- [x] JSON and CSV reporting
- [x] URL-based evidence collection
- [x] Unified operations endpoint

### Phase 2 — AI and Agent Orchestration

- [ ] LangGraph-based orchestration
- [ ] More robust multi-agent coordination
- [ ] Agent state management
- [ ] Structured agent communication
- [ ] Tool execution policies
- [ ] Agent evaluation framework

### Phase 3 — Retrieval and Intelligence

- [ ] Retrieval-Augmented Generation (RAG)
- [ ] Persistent vector database integration
- [ ] Document ingestion pipeline
- [ ] Semantic search
- [ ] Evidence citation and verification improvements

### Phase 4 — Engineering and Production

- [ ] Authentication and authorization
- [ ] Role-based access control
- [ ] Improved database architecture
- [ ] Background task processing
- [ ] Observability and structured logging
- [ ] API rate limiting
- [ ] Security hardening
- [ ] Expanded automated test coverage
- [ ] Production deployment support

---

## Contributing

Contributions, ideas, bug reports, and improvements are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement your changes.
4. Add or update tests.
5. Run the test suite.
6. Submit a pull request.

Example:

```bash
git checkout -b feature/your-feature
```

```bash
git add .
git commit -m "Add: your feature"
git push origin feature/your-feature
```

Open a pull request against the `main` branch.

---

## Open Source

FlowReign AI is intended to be developed as an open-source project.

The repository was initialized with an MIT license selection. Ensure the actual `LICENSE` file is present in the repository before describing the project as MIT-licensed.

---

## Project Information

**Project:** FlowReign AI  
**Tagline:** Intelligence That Executes.  
**Category:** AI / GenAI / Workflow Automation / Business Operations Intelligence  
**Development Stage:** MVP / Active Development

**Maintainer:** Manikanta Banavathu

- GitHub: https://github.com/Manikanta-23-ai
- Repository: https://github.com/Manikanta-23-ai/flowreign-ai
- Website: https://manikanta-23-ai.github.io/flowreign-ai/

---

## Vision

The future of business operations is not simply about generating answers. It is about connecting intelligence to structured execution.

FlowReign AI explores that direction by combining workflow systems, data intelligence, evidence collection, specialist AI components, and human oversight in one extensible open-source platform.

**Plan intelligently. Execute systematically. Keep humans in control.**

---

<p align="center">
  <strong>FLOWREIGN AI</strong><br>
  Intelligence That Executes.
</p>
