# Check Perplexity Access via Comet Browser Student Enrollment

## Option 1: Check Comet Dashboard

1. Log into your Comet browser account
2. Go to Settings or Account Dashboard
3. Look for "API Access" or "Developer Settings"
4. Check if Perplexity API is included in your student plan

## Option 2: Try Perplexity Directly

1. Go to: https://www.perplexity.ai/
2. Sign in with your student email
3. Check if you have API access under Settings → API

## Option 3: Perplexity Education Program

1. Go to: https://www.perplexity.ai/hub/getting-started/perplexity-api
2. Check if they have student/education pricing
3. Sign up with your .edu email

## Option 4: Use Free Alternative (Tavily)

If Perplexity isn't free:
- Tavily has a generous free tier (1000 requests/month)
- Sign up at: https://tavily.com/
- Specifically built for AI/LLM use cases

## How to Integrate Perplexity

Once you have API access:

### 1. Get API Key
- From Perplexity dashboard
- Format: `pplx-xxxxxxxxxx`

### 2. Add to .env
```bash
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxx
```

### 3. Update main.py
```python
# In backend/main.py line 60:
from services.web_search_improved import ImprovedWebSearchService
web_search_service = ImprovedWebSearchService()
```

The improved web search will automatically detect and use Perplexity!

### 4. Restart Backend
```bash
cd backend
..\venv\Scripts\python.exe main.py
```

You should see:
```
[WEB SEARCH] Initialized with provider: perplexity
```

## Benefits of Perplexity for SFSU Search

1. **AI-Native**: Designed for AI assistants like yours
2. **Built-in Citations**: Returns sources automatically
3. **Clean Data**: No HTML parsing needed
4. **SFSU-Focused**: Can search specifically for SFSU content
5. **Recent Info**: Always current data

## Test It

Ask your chatbot:
- "What are the application deadlines for Fall 2025?"
- "What's the latest news from SFSU?"
- "What are current tuition costs?"

All answers should cite [Web] source with Perplexity data!
