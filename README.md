# Demo Gauntlet 🛡️

**Demo Gauntlet** is an AI-powered simulation environment designed to help Solution Consultants and Sales Engineers practice their demo skills. It ingests a sales deck, researches the prospect/industry, and generates dynamic "Challenger Personas" (e.g., Skeptical CTO, ROI-focused CFO) to grill the user with tough questions.

## 🚀 Features

-   **Deck Ingestion**: Upload PDF or PPTX decks. The system parses text and slides.
-   **AI Research Agent**: Automatically researches competitors, industry trends, and compliance risks based on the deck content.
-   **Challenger Personas**: Simulates realistic stakeholders (CTO, CFO, CMO) with distinct personalities and concerns.
-   **Real-time Evaluation**: Scores answers on the fly using an LLM-based evaluation engine with server-side ideal answer lookup.
-   **Session Reporting**: Generates a detailed report card with strengths, weaknesses, and a readiness score.
-   **Security**: JWT-authenticated API, server-side scoring, upload size limits, per-session guest isolation.

## 🛠️ Tech Stack

-   **Backend**: Python, FastAPI, ChromaDB (Vector Store), Arq + Redis (background processing).
-   **Frontend**: React, TypeScript, Vite, TailwindCSS.
-   **AI**: Anthropic Claude (primary), OpenAI (optional fallback).
-   **Search**: Brave Search (optional).

## 📦 Installation

### Prerequisites
-   Python 3.10+
-   Node.js 18+
-   Redis (for background deck processing)
-   Anthropic API Key (`ANTHROPIC_API_KEY`)
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

# Configure environment
cp .env.example .env
# Edit .env and set at minimum:
#   ANTHROPIC_API_KEY — required for all LLM calls
#   SECRET_KEY        — required; any random string (e.g. openssl rand -hex 32)
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Optional: Demo Auto-Login
To enable the one-click demo login (auto-submits a guest session with a preset code):

```bash
# In .env (backend):
BETA_INVITE_CODE=your-invite-code

# In frontend/.env (or set as build env var):
VITE_DEMO_INVITE_CODE=your-invite-code
```

When `VITE_DEMO_INVITE_CODE` is set, the app automatically calls `/auth/login` with that code on page load. If the variable is not set, users must enter the code manually.

## 🏃‍♂️ Usage

### Run the Application

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

-   **Authentication**: All API endpoints that generate LLM calls or mutate data require a valid JWT. Tokens are issued by `/auth/login` and must be passed as `Authorization: Bearer <token>`.
-   **Secret Key**: `SECRET_KEY` is used to sign JWTs. If the default value is detected at startup, the application logs a loud `WARNING`. In production (`ENV_MODE=production`) it refuses to start. Set this to any strong random value before exposing the service externally.
-   **Upload Limits**: File uploads are capped at 50 MB (HTTP 413 if exceeded).
-   **Server-Side Scoring**: Ideal answers are looked up server-side only; the client never controls the grading key.
-   **CORS**: By default, the API only accepts requests from `http://localhost:5173`. Update `ALLOWED_ORIGINS` in `.env` for production.
-   **Data**: Uploaded decks are stored in `data/decks`. Ensure this directory is secured in production.

## 📄 License
MIT
