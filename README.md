# SFSU CS Chatbot (Alli) 🐊

**AI-powered chatbot for San Francisco State University Computer Science students**

A production-ready RAG (Retrieval-Augmented Generation) chatbot featuring dual-source retrieval, professor correction workflow, zero-hallucination architecture, and real-time web search capabilities.

## Features

- **Dual-Source RAG**: Parallel retrieval from vector database (28,541 SFSU documents) and real-time web search
- **Zero-Hallucination Architecture**: Temperature 0.0, mandatory source citations, response validation
- **Professor Correction Workflow**: Professors can review and correct bot responses
- **Student Notifications**: Real-time notifications when professors update flagged responses
- **Authentication System**: Secure JWT-based authentication for professors
- **Response Caching**: LRU cache for improved performance
- **Rate Limiting**: Built-in protection against API abuse
- **Local LLM Support**: Ollama integration for unlimited requests without API costs

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **LLM**: Ollama (local) / Groq (cloud)
- **Database**: Supabase (PostgreSQL with pgvector)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Web Search**: SerpAPI
- **Authentication**: JWT (python-jose)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Routing**: React Router v7
- **UI Components**: Framer Motion, Lucide Icons

## Project Structure

```
sfsu-cs-chatbot/
├── backend/                    # Backend API
│   ├── main.py                # FastAPI application entry point
│   └── services/              # Service modules
│       ├── auth.py           # JWT authentication
│       ├── database.py       # Supabase integration
│       ├── rag.py            # RAG retrieval
│       ├── web_search.py     # Web search integration
│       ├── llm.py            # Groq LLM service
│       ├── llm_ollama.py     # Ollama LLM service
│       ├── dual_source_rag.py    # Dual-source retrieval
│       ├── context_merger.py     # Context merging logic
│       ├── cache.py          # Response caching
│       ├── email.py          # Email OTP service
│       └── ...
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   │   ├── LandingPage.jsx
│   │   │   ├── StudentChat.jsx
│   │   │   ├── ProfessorLogin.jsx
│   │   │   └── ProfessorDashboard.jsx
│   │   ├── components/       # Reusable components
│   │   └── services/         # API client
│   └── package.json
├── database/                   # Database schemas and migrations
│   ├── schema.sql
│   ├── migrate_data.py
│   └── ...
├── data/                       # Scraped SFSU data (JSON files)
│   ├── sfsu_ultimate_crawl.json
│   └── ...
├── tests/                      # Test files
│   ├── test_backend.py
│   ├── test_chatbot.py
│   ├── test_dual_source_system.py
│   └── ...
├── scripts/                    # Utility scripts
│   ├── migration/             # Data migration scripts
│   ├── data_generation/       # Scraping and QA generation
│   └── admin/                 # Admin utilities
├── tools/                      # Deployment and AWS tools
├── docs/                       # Documentation
└── archive/                    # Legacy code (for reference)
```

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Ollama (for local LLM) OR Groq API key (for cloud LLM)
- Supabase account
- SerpAPI key (for web search)

### Backend Setup

1. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the project root:
```env
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# LLM (choose one)
GROQ_API_KEY=your_groq_api_key  # For cloud LLM
OLLAMA_API_URL=http://localhost:11434  # For local LLM

# Web Search
SERPAPI_KEY=your_serpapi_key

# JWT Authentication
SECRET_KEY=your_secret_key_here

# Email (optional - for OTP)
RESEND_API_KEY=your_resend_api_key
```

4. **Run backend**
```bash
cd backend
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure API URL**
Update `frontend/src/services/api.js` if needed:
```javascript
const API_BASE_URL = "http://localhost:8000";
```

3. **Run development server**
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

### For Students

1. Visit the landing page
2. Click "Chat with Alli"
3. Ask questions about SFSU CS department, courses, admissions, etc.
4. Flag incorrect responses for professor review
5. Receive notifications when professors correct responses

### For Professors

1. Register using your SFSU email
2. Verify email with OTP
3. Login to access the dashboard
4. Review flagged responses from students
5. Approve, correct, or reject flagged content
6. View analytics and trending questions

## Testing

### Run Backend Tests
```bash
# Test backend services
python tests/test_backend.py

# Test dual-source RAG system
python tests/test_dual_source_system.py

# Test anti-hallucination features
python tests/test_anti_hallucination.py

# Test database connection
python tests/test_db_connection.py
```

### Test Chatbot
```bash
# Interactive chatbot test
python tests/test_chatbot.py
```

## Scripts

### Data Migration
```bash
# Migrate scraped data to Supabase
python scripts/migration/migrate_simple.py

# Load specific JSON file
python scripts/migration/load_scraped_data_to_supabase.py
```

### Data Generation
```bash
# Scrape SFSU website
python scripts/data_generation/scrape_ultimate_sfsu.py

# Generate QA training data
python scripts/data_generation/generate_qa_with_ollama.py
```

### Admin Tools
```bash
# Add admin professor
python scripts/admin/add_admin.py

# Check document quality
python scripts/admin/check_document_quality.py

# List all database tables
python scripts/admin/list_all_tables.py
```

## Documentation

See the `docs/` directory for detailed guides:

- **Deployment**: `DEPLOY_NOW.md`, `FREE_DEPLOYMENT_OPTIONS.md`
- **Anti-Hallucination**: `ZERO_PERCENT_HALLUCINATION_GUIDE.md`
- **Authentication**: `AUTHENTICATION_GUIDE.md`
- **Ollama Setup**: `OLLAMA_SETUP_COMPLETE.md`
- **Dual-Source System**: `DUAL_SOURCE_IMPLEMENTATION.md`

## API Endpoints

### Public Endpoints (Students)

- `GET /` - Health check
- `POST /chat` - Chat with the bot
- `POST /flag-incorrect` - Flag incorrect response
- `GET /corrections/{id}` - View correction details
- `POST /feedback` - Submit feedback (thumbs up/down)
- `GET /notifications/{session_id}` - Get notifications

### Professor Endpoints (Auth Required)

- `POST /professor/login` - Login
- `POST /professor/register` - Register
- `GET /professor/corrections` - Get pending corrections
- `PUT /professor/corrections/{id}` - Review correction
- `GET /professor/analytics` - View analytics
- `GET /professor/trending-questions` - View trending queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Update tests if needed
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [Report here](https://github.com/yourusername/sfsu-cs-chatbot/issues)
- Email: your-email@sfsu.edu

## Acknowledgments

- San Francisco State University Computer Science Department
- Built with Claude Code
- Data sources: SFSU official websites and bulletin

---

**Version**: 2.0.0
**Last Updated**: January 2025
