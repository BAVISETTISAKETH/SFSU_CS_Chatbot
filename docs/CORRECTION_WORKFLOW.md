# Correction Workflow Documentation

## Overview
This document explains the complete correction workflow for the SFSU CS Chatbot, from when a student flags an incorrect response to when the corrected response is used in future queries.

---

## Complete Workflow

### 1️⃣ Student Flags Incorrect Response

**Location:** `frontend/src/pages/StudentChat.jsx`

1. Student asks a question and receives a response from Alli
2. If the response is incorrect, student clicks "Flag as incorrect" button
3. A dialog appears asking for the reason
4. Student provides reason and clicks "Submit"

**Frontend Code:**
```javascript
const submitFlag = async () => {
  await flagIncorrect(userQuery, flaggedMessage.content, flagReason);
  alert('Thank you! A professor will review this response.');
};
```

**API Call:** `POST /corrections/flag`
```json
{
  "query": "What is CPT?",
  "response": "CPT stands for Computer Programming Technology...",
  "reason": "CPT actually means Curricular Practical Training"
}
```

---

### 2️⃣ Correction Saved to Database

**Location:** `backend/main.py` → `/corrections/flag` endpoint

The flagged response is saved to the `corrections` table:
- `student_query` - The question student asked
- `rag_response` - The incorrect response bot gave
- `category` - Student's reason for flagging
- `status` - Set to "pending"

**Database Table:** `corrections`
```sql
CREATE TABLE corrections (
    id SERIAL PRIMARY KEY,
    student_query TEXT NOT NULL,
    rag_response TEXT NOT NULL,
    professor_correction TEXT,
    category TEXT,
    status TEXT DEFAULT 'pending',
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3️⃣ Professor Views Pending Corrections

**Location:** `frontend/src/pages/ProfessorDashboard.jsx`

1. Professor logs in and navigates to dashboard
2. Dashboard shows all pending corrections
3. Each correction displays:
   - Student's original query
   - Bot's response
   - Student's reason for flagging

**API Call:** `GET /professor/corrections/pending`
```json
[
  {
    "_id": "123",
    "query": "What is CPT?",
    "botResponse": "CPT stands for Computer Programming Technology...",
    "reason": "CPT actually means Curricular Practical Training",
    "created_at": "2024-10-11T10:30:00Z"
  }
]
```

---

### 4️⃣ Professor Reviews & Takes Action

The professor has **3 options**:

#### Option A: Approve (Response is Correct)
- Professor clicks "Approve" button
- Original response is stored as a verified fact
- Status updated to "approved"

#### Option B: Correct (Edit Response)
- Professor clicks "Correct" button
- Textarea becomes editable
- Professor edits the response
- Professor clicks "Submit Correction"
- **Edited response** is stored as a verified fact
- Status updated to "approved"

#### Option C: Reject (Response is Wrong, No Correction)
- Professor clicks "Reject" button
- Correction is marked as rejected
- No verified fact is created

**Frontend Code:**
```javascript
const handleReview = async (correctionId, action, correctedText = '') => {
  await reviewCorrection(correctionId, action, correctedText);
  await loadData(); // Refresh the list
};
```

**API Call:** `POST /professor/corrections/{id}/review`
```json
{
  "action": "approve",
  "corrected_response": "CPT (Curricular Practical Training) is work authorization..."
}
```

---

### 5️⃣ Backend Processes Professor's Review

**Location:** `backend/main.py` → `/professor/corrections/{id}/review` endpoint

#### When Action = "approve":
1. Retrieve the correction from database
2. Determine final answer:
   - If `corrected_response` provided → use edited version
   - If no `corrected_response` → use original bot response
3. **Store in `verified_facts` table** with embedding
4. Update correction status to "approved"

**Code:**
```python
if request.action == 'approve':
    final_answer = request.corrected_response if request.corrected_response else correction['rag_response']

    # Store in verified_facts
    await db_service.add_verified_fact(
        question=correction['student_query'],
        answer=final_answer,
        verified_by=professor['email'],
        category=correction.get('category')
    )
```

**Database Table:** `verified_facts`
```sql
CREATE TABLE verified_facts (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding VECTOR(384),
    category TEXT,
    verified_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 6️⃣ Verified Fact is Stored with Vector Embedding

**Location:** `backend/services/database.py` → `add_verified_fact()`

1. Generate embedding for the question using sentence-transformers
2. Insert into `verified_facts` table
3. Embedding allows semantic search (similar questions match)

**Code:**
```python
async def add_verified_fact(self, question, answer, verified_by, category):
    embedding = self.embedding_model.encode(question).tolist()

    self.client.table("verified_facts").insert({
        "question": question,
        "answer": answer,
        "embedding": embedding,
        "category": category,
        "verified_by": verified_by
    }).execute()
```

---

### 7️⃣ Future Student Query Retrieves Verified Fact

**Location:** `backend/main.py` → `/chat` endpoint

When a student asks a question, the system follows this priority:

```
1. Search verified_facts (highest priority)
   ├─ If found with confidence > 0.75 → Return professor's answer ✅
   └─ If not found → Continue to step 2

2. Search RAG documents (knowledge base)
   ├─ If confidence > 0.6 → Return RAG answer
   └─ If confidence < 0.6 → Continue to step 3

3. Use Web Search (lowest priority)
   └─ Return web search enhanced answer
```

**Code Flow:**
```python
# Step 1: Check verified facts (highest priority)
verified_result = await rag_service.search_verified_facts(request.query)

if verified_result and verified_result['confidence'] > 0.75:
    return ChatResponse(
        response=verified_result['answer'],
        source='verified_fact',
        confidence=verified_result['confidence'],
        sources=[{"type": "verified_fact", "verified_by": verified_result.get('verified_by')}]
    )
```

---

### 8️⃣ Vector Similarity Search

**Location:** `backend/services/database.py` → `search_verified_facts()`

The system uses **cosine similarity** to find matching verified facts:

1. Convert student query to embedding vector
2. Call database function `match_verified_facts`
3. Returns matches with similarity score (0-1)
4. Only returns if similarity > 0.7 (70% match)

**Similar Questions That Match:**
- Original: "What is CPT for international students?"
- Matches:
  - "Tell me about CPT" (0.85 similarity)
  - "CPT application process" (0.78 similarity)
  - "How to apply for CPT" (0.76 similarity)

---

## Database Schema

### Corrections Table
```sql
CREATE TABLE corrections (
    id SERIAL PRIMARY KEY,
    student_query TEXT NOT NULL,
    rag_response TEXT NOT NULL,
    professor_correction TEXT,
    category TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    reviewed_by TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Verified Facts Table
```sql
CREATE TABLE verified_facts (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding VECTOR(384),  -- Sentence-transformer embedding
    category TEXT,
    verified_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for fast vector search
CREATE INDEX ON verified_facts USING ivfflat (embedding vector_cosine_ops);
```

### Match Function (Supabase)
```sql
CREATE OR REPLACE FUNCTION match_verified_facts(
    query_embedding VECTOR(384),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id BIGINT,
    question TEXT,
    answer TEXT,
    category TEXT,
    verified_by TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        verified_facts.id,
        verified_facts.question,
        verified_facts.answer,
        verified_facts.category,
        verified_facts.verified_by,
        1 - (verified_facts.embedding <=> query_embedding) AS similarity
    FROM verified_facts
    WHERE 1 - (verified_facts.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

---

## API Endpoints Summary

### Student Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Ask question to chatbot |
| `/corrections/flag` | POST | Flag incorrect response |

### Professor Endpoints (Requires Auth)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/professor/login` | POST | Login |
| `/professor/corrections/pending` | GET | Get pending corrections |
| `/professor/corrections/{id}/review` | POST | Approve/reject/correct |
| `/professor/stats` | GET | Get analytics |

---

## Testing the Workflow

### Manual Testing Steps:

1. **Start Backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test as Student:**
   - Ask: "What is CPT?"
   - Flag the response as incorrect
   - Provide reason

4. **Test as Professor:**
   - Login to professor dashboard
   - View pending corrections
   - Edit response or approve
   - Submit

5. **Verify Storage:**
   - Ask same question again
   - Should receive professor's corrected answer
   - Response should show `source: 'verified_fact'`

### Automated Testing:

Run the test script:
```bash
python test_correction_workflow.py
```

This will:
1. Create a test correction
2. Add a verified fact
3. Search for the verified fact
4. Verify similarity matching works
5. Clean up test data

---

## Key Features

✅ **Priority System:** Verified facts checked first, then RAG, then web search
✅ **Semantic Matching:** Similar questions match using vector similarity
✅ **Professor Attribution:** Each verified fact shows who approved it
✅ **Edit Capability:** Professors can correct responses before approving
✅ **Confidence Scoring:** Only high-confidence matches (>0.75) are used
✅ **Audit Trail:** All corrections tracked with timestamps and reviewer info

---

## Future Enhancements

- [ ] Allow professors to edit existing verified facts
- [ ] Show students when they receive a verified fact (badge/indicator)
- [ ] Add bulk import for verified facts
- [ ] Export verified facts as JSON/CSV
- [ ] Professor dashboard to manage all verified facts
- [ ] Student feedback on verified facts (helpful/not helpful)

---

## Troubleshooting

### Verified Facts Not Being Retrieved
1. Check if fact was actually saved: Query `verified_facts` table
2. Check similarity threshold: Lower from 0.75 to 0.65 for testing
3. Test embedding: Ensure sentence-transformers model is working
4. Check database function: Ensure `match_verified_facts` exists

### Corrections Not Showing in Dashboard
1. Verify correction was saved: Check `corrections` table
2. Check auth token: Ensure professor is logged in
3. Check endpoint: Frontend should call `/professor/corrections/pending`
4. Check status filter: Only shows `status = 'pending'`

---

**Last Updated:** October 11, 2025
**Version:** 1.0
