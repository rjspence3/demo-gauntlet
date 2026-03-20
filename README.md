# Demo Gauntlet 🛡️

**Demo Gauntlet** is an AI-powered simulation environment designed to help Solution Consultants and Sales Engineers practice their demo skills. It ingests a sales deck, researches the prospect/industry, and generates dynamic "Challenger Personas" (e.g., Skeptical CTO, ROI-focused CFO) to grill the user with tough questions.

## 🚀 Features

-   **Deck Ingestion**: Upload PDF or PPTX decks. The system parses text and slides.
-   **AI Research Agent**: Automatically researches competitors, industry trends, and compliance risks based on the deck content.
-   **Challenger Personas**: Simulates realistic stakeholders (CTO, CFO, CMO) with distinct personalities and concerns.
-   **Real-time Evaluation**: Scores your answers on the fly using an LLM-based evaluation engine.
-   **Session Reporting**: Generates a detailed report card with strengths, weaknesses, and a readiness score.
-   **Security**: Built with security in mind (CORS restrictions, sanitized uploads, server-side scoring).

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, LangChain (or direct LLM calls), ChromaDB (Vector Store).
-   **Frontend**: React, TypeScript, Vite, TailwindCSS (or custom CSS).
-   **AI**: OpenAI GPT-4o (configurable).
-   **Search**: Brave Search / SerpAPI (optional).

## 📦 Installation

### Prerequisites
-   Python 3.10+
-   Node.js 18+
-   OpenAI API Key
-   **OCR Dependencies** (for slide parsing):
    -   `poppler` (macOS: `brew install poppler`, Ubuntu: `sudo apt-get install poppler-utils`)
    -   `tesseract` (macOS: `brew install tesseract`, Ubuntu: `sudo apt-get install tesseract-ocr`)

### 1. Clone the Repository
```bash
git clone https://github.com/rjspence3/demo-gauntlet.git
cd demoGauntlet
```

### 2. Backend Setup
```bash
# Create virtual environment and install dependencies
make install

# Configure Environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

## 🏃‍♂️ Usage

### Run the Application
You can run both backend and frontend using the Makefile:

```bash
# Terminal 1: Backend
make run-backend

# Terminal 2: Frontend
make run-frontend
```

Access the application at `http://localhost:5173`.

-   **Backend API**: `http://localhost:8001`

### Development
-   **Linting**: `make lint`
-   **Type Checking**: `make typecheck`
-   **Testing**: `make test`

## 🛡️ Security Notes
-   **CORS**: By default, the API only accepts requests from `http://localhost:5173`. Update `ALLOWED_ORIGINS` in `backend/config.py` for production.
-   **Data**: Uploaded decks are stored in `data/decks`. Ensure this directory is secured in production.

## 📄 License
MIT

