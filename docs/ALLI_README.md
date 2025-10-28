# 🟣🟡 Alli - SFSU CS Chatbot

## Website Name Suggestions:

1. **"Gator Guide"** (SFSU mascot is the Gator) ⭐ RECOMMENDED
2. **"CS Compass"** - Navigate your CS journey
3. **"Tech Talk SFSU"** - Your CS department assistant
4. **"Golden Gate CS"** - SF + CS reference
5. **"Purple Path"** - SFSU colors + guidance

**Recommended: "Gator Guide" - powered by Alli**
- Catchy and memorable for SFSU students
- References the school mascot (Gators)
- Easy to say and spell
- Professional yet approachable

---

## 🤖 Meet Alli

**Alli** is your friendly AI assistant for the SFSU Computer Science Department!

### Personality:
- Warm, enthusiastic upperclassman vibe
- Genuinely excited about helping students succeed
- Casual but professional tone
- Empathetic and understanding of student challenges
- Uses SFSU purple 💜 and gold 💛

### Capabilities:
1. **RAG (Retrieval-Augmented Generation)**
   - Searches vector database of SFSU CS content
   - Provides context-aware, accurate answers
   - Cites sources for transparency

2. **Web Search Integration**
   - Falls back to web search for current info
   - Combines knowledge base + live web data
   - Perfect for events, news, schedule changes

3. **Professor Correction Workflow**
   - Students can flag incorrect responses
   - Professors review and approve/correct
   - Verified facts get highest priority in future queries
   - Continuous improvement loop

4. **Analytics Dashboard**
   - Track usage patterns
   - Monitor correction requests
   - Measure response quality
   - Identify knowledge gaps

---

## 📊 Data Sources

### 1. Web Scraped Data
- **Source**: Official SFSU CS website
- **Content**: Department info, news, resources, bulletin
- **Documents**: ~4 pages (expandable)

### 2. Course Catalog
- **Source**: SFSU CS course offerings
- **Content**: Course codes, titles, descriptions, units
- **Courses**: 8+ core CS courses

### 3. Custom Knowledge Base
- **Source**: Your existing JSON files
- **Content**: Department-specific Q&A, FAQs, policies
- **Flexible**: Easy to add more data

---

## 🎨 Design System

### Colors (Official SFSU)
```css
Primary Purple: #4B2E83
Primary Gold: #B4975A

Supporting Purples:
- Light: #6B4FA3
- Lighter: #8B70B8
- Dark: #3A2366
- Darker: #2A1A4D

Supporting Golds:
- Light: #C9AD74
- Lighter: #DCC890
- Dark: #9B7F47
- Darker: #826935

Complementary:
- Cream: #F5F3ED
- Charcoal: #2C2C2E
- Slate: #1E1E24
```

### Typography
- **Headings**: Bold, gradient purple-to-gold
- **Body**: Clean, readable white/cream on dark
- **Accent**: Gold for highlights, purple for CTAs

### Effects
- Glass morphism UI
- Smooth gradients
- Animated floating orbs
- Subtle hover effects
- Shadow layers for depth

---

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
backend/
├── main.py              # FastAPI app, routes, middleware
├── services/
│   ├── llm.py          # Groq LLM (Llama 3.3 70B) - Alli's brain
│   ├── rag.py          # Retrieval & context preparation
│   ├── database.py     # Supabase integration
│   ├── web_search.py   # SerpAPI for web results
│   └── auth.py         # Professor authentication
└── .env                # API keys & config
```

### Frontend (React + Vite + TailwindCSS)
```
frontend/
├── src/
│   ├── pages/
│   │   ├── StudentChat.jsx          # Main chat interface
│   │   ├── ProfessorLogin.jsx       # Auth page
│   │   ├── ProfessorDashboard.jsx   # Correction management
│   │   └── LandingPage.jsx          # Split-screen entry
│   ├── services/
│   │   └── api.js                   # API client
│   ├── App.jsx                      # Router
│   ├── index.css                    # SFSU-branded styles
│   └── main.jsx                     # Entry point
└── tailwind.config.js               # SFSU color palette
```

### Database (Supabase + pgvector)
```sql
Tables:
- documents           # Vector-indexed knowledge base
- verified_facts      # Professor-approved answers
- corrections         # Flagged responses for review
- professors          # Auth & permissions
- chat_logs           # Analytics & monitoring
- web_search_cache    # Performance optimization
```

---

## 🚀 Features Implemented

### ✅ Student Features
- [x] Real-time chat with Alli
- [x] Intelligent query routing (verified → RAG → web)
- [x] Source citations
- [x] Flag incorrect responses
- [x] Beautiful SFSU-branded UI
- [x] Mobile-responsive design
- [x] Session persistence
- [x] Typing indicators
- [x] Message animations

### ✅ Professor Features
- [x] Secure login (JWT)
- [x] Review flagged responses
- [x] Approve/correct/reject workflow
- [x] Add verified facts
- [x] Analytics dashboard
- [x] Real-time stats

### ✅ Backend Features
- [x] Vector similarity search (pgvector)
- [x] Groq LLM integration (Llama 3.3 70B)
- [x] SerpAPI web search
- [x] Sentence transformers (embeddings)
- [x] Professor authentication
- [x] CORS configuration
- [x] Error handling
- [x] Request logging
- [x] Async operations

### ✅ Data Pipeline
- [x] Web scraper for SFSU CS site
- [x] Course catalog integration
- [x] JSON data migration
- [x] Vector embedding generation
- [x] Batch upload to Supabase
- [x] Duplicate prevention

---

## 📝 Environment Variables Needed

```bash
# .env file

# Groq LLM
GROQ_API_KEY=gsk_...

# Supabase
SUPABASE_URL=https://....supabase.co
SUPABASE_KEY=eyJ...

# SerpAPI (for web search)
SERPAPI_KEY=...

# JWT Secret (for professor auth)
JWT_SECRET=your_secure_random_string

# Optional
NODE_ENV=development
```

---

## 🎯 Next Steps to Deploy

### 1. Run Data Migration
```bash
# Activate virtual environment
venv\Scripts\activate

# Run complete migration
python migrate_complete.py
```

### 2. Test Backend
```bash
cd backend
python main.py

# Visit: http://localhost:8000
# Test: http://localhost:8000/chat
```

### 3. Test Frontend
```bash
cd frontend
npm install
npm run dev

# Visit: http://localhost:5173
```

### 4. Deploy Backend
**Option A: Railway**
- Connect GitHub repo
- Add environment variables
- Deploy automatically

**Option B: Render**
- Create web service
- Connect repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Deploy Frontend
**Option A: Vercel** (Recommended)
```bash
cd frontend
npm install -g vercel
vercel
```

**Option B: Netlify**
- Connect GitHub repo
- Build command: `npm run build`
- Publish directory: `dist`

---

## 🧪 Testing Alli

### Test Queries:
1. "What CS courses does SFSU offer?"
2. "Tell me about CSC 317"
3. "Who are the CS professors?"
4. "What are the requirements for the CS major?"
5. "When is the next CS event?"
6. "How do I apply to the CS program?"

### Expected Behavior:
- Alli responds warmly and enthusiastically
- Uses "Hey!", "I'm here to help!", etc.
- Cites sources when appropriate
- Falls back to web search for current events
- Suggests next steps or resources

---

## 🎓 Alli's Voice Examples

**Course Question:**
> "Hey! CSC 317 (Web Development) is an awesome hands-on course! It covers full-stack web development using modern frameworks. It's 3 units and super practical for real-world skills. Want to know about prerequisites or what projects you'll build? 💜"

**General Question:**
> "Great question! Let me pull up the latest info for you... According to the CS Department website, [answer]. Need more details about this? I'm here for you!"

**Missing Information:**
> "Hmm, I don't have that specific info in my database right now, but I can help you find it! Try contacting the CS department at cs@sfsu.edu or visiting their office in Thornton Hall. Anything else I can help with? 💛"

---

## 📊 Performance Metrics

**Response Time Goals:**
- RAG queries: < 2s
- Web search queries: < 5s
- Verified facts: < 1s

**Accuracy Goals:**
- Verified facts: 100%
- RAG responses: > 90%
- Web-enhanced: > 85%

**User Experience:**
- Mobile responsive: ✅
- Accessibility: WCAG 2.1 AA compliant
- Load time: < 3s initial
- Interactive: < 100ms

---

## 🔧 Maintenance

### Weekly:
- Review flagged responses
- Update verified facts
- Check analytics

### Monthly:
- Re-scrape SFSU website
- Update course catalog
- Review popular queries
- Optimize prompts

### Quarterly:
- Model evaluation
- Performance tuning
- Feature requests
- User feedback integration

---

## 💡 Future Enhancements

1. **Multi-modal Support**
   - Image uploads (homework, diagrams)
   - PDF document analysis
   - Voice input

2. **Personalization**
   - Student profiles
   - Course recommendations
   - Career path suggestions

3. **Integrations**
   - Canvas LMS
   - SFSU calendar
   - Registration system

4. **Advanced Features**
   - Study group matching
   - Office hours scheduler
   - Assignment help

5. **Expanded Data**
   - All SFSU departments
   - Student handbook
   - Campus resources

---

## 🙏 Credits

**Built with:**
- 🤖 Groq (Llama 3.3 70B)
- 🗄️ Supabase (PostgreSQL + pgvector)
- ⚡ FastAPI
- ⚛️ React + Vite
- 🎨 TailwindCSS
- 🔍 SerpAPI
- 🧠 Sentence Transformers

**For:**
- San Francisco State University
- Computer Science Department
- SFSU Students, Faculty, and Staff

---

## 📞 Support

For questions or issues:
- Email: cs@sfsu.edu
- SFSU CS Website: https://cs.sfsu.edu
- GitHub Issues: [your-repo-url]

---

**Made with 💜💛 for SFSU Gators!**
