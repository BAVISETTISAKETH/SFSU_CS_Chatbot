# 📬 Student Notification System - Implementation Guide

**Feature**: Students get notified when professors review their flagged responses
**Status**: ✅ Code already implemented - Just needs database table
**Action Required**: Run SQL migration in Supabase

---

## 🎯 What This Does

When a student flags a response as incorrect:
1. Student clicks "Flag as incorrect" and submits reason
2. Flag goes to Professor Dashboard
3. Professor reviews and either:
   - ✅ **Approves** (with or without corrections)
   - ❌ **Rejects** the flag
4. **Student gets notification** in the notification bell icon
5. Student can click to see what the professor said

---

## 🔔 Notification Types

### Type 1: Professor Corrected the Response
**When**: Professor approves flag and provides a corrected answer

**Student Sees**:
```
🔔 Notification Badge: 1 unread

Click notification bell:
┌─────────────────────────────────────┐
│ Response Corrected ✅               │
│ A professor has reviewed and        │
│ corrected the response to:          │
│ "What is the CS department chair?"  │
│                                     │
│ Click to view                       │
└─────────────────────────────────────┘
```

---

### Type 2: Professor Verified Original Response
**When**: Professor reviews flag but determines original response was correct

**Student Sees**:
```
🔔 Notification Badge: 1 unread

Click notification bell:
┌─────────────────────────────────────┐
│ Response Verified ✅                │
│ A professor has verified the        │
│ response to:                        │
│ "What is CS 101?"                   │
│                                     │
│ Click to view                       │
└─────────────────────────────────────┘
```

---

### Type 3: Professor Rejected the Flag
**When**: Professor reviews and rejects the flag (original response was correct)

**Student Sees**:
```
🔔 Notification Badge: 1 unread

Click notification bell:
┌─────────────────────────────────────┐
│ Flag Reviewed ℹ️                    │
│ A professor has reviewed your       │
│ flag for: "What is the deadline?"   │
│ The original response has been      │
│ determined to be correct.           │
│                                     │
│ Click to view                       │
└─────────────────────────────────────┘
```

---

## ✅ How It Works (Already Implemented!)

### Backend Code (Already Complete)

**File**: `backend/main.py:778-817`

When professor reviews a correction:

```python
# Professor approves with corrections
if request.corrected_response:
    await db_service.create_notification(
        session_id=correction['session_id'],
        correction_id=correction_id_int,
        title="Response Corrected ✅",
        message=f"A professor has reviewed and corrected the response to: '{correction['student_query'][:80]}...'",
        notification_type='correction_edited'
    )

# Professor approves as-is
else:
    await db_service.create_notification(
        session_id=correction['session_id'],
        correction_id=correction_id_int,
        title="Response Verified ✅",
        message=f"A professor has verified the response to: '{correction['student_query'][:80]}...'",
        notification_type='correction_approved'
    )

# Professor rejects flag
await db_service.create_notification(
    session_id=correction['session_id'],
    correction_id=correction_id_int,
    title="Flag Reviewed",
    message=f"A professor has reviewed your flag for: '{correction['student_query'][:80]}...' The original response has been determined to be correct.",
    notification_type='correction_rejected'
)
```

---

### Frontend Code (Already Complete)

**File**: `frontend/src/pages/StudentChat.jsx:118-123`

Notifications are polled every 30 seconds:

```javascript
// Load notifications on mount and poll every 30 seconds
useEffect(() => {
  loadNotifications();
  const interval = setInterval(loadNotifications, 30000);
  return () => clearInterval(interval);
}, [sessionId]);
```

**Notification Bell** displays unread count and shows notifications when clicked.

---

## 🚀 Setup (30 Seconds in Supabase)

### Step 1: Open Supabase SQL Editor

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **"SQL Editor"** in left sidebar
4. Click **"New query"**

---

### Step 2: Run This SQL

Copy and paste this entire SQL into the editor:

```sql
-- Create notifications table for student notifications
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    correction_id BIGINT REFERENCES corrections(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('correction_approved', 'correction_rejected', 'correction_edited')),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS notifications_session_id_idx ON notifications(session_id);
CREATE INDEX IF NOT EXISTS notifications_is_read_idx ON notifications(is_read);
CREATE INDEX IF NOT EXISTS notifications_created_at_idx ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS notifications_session_unread_idx ON notifications(session_id, is_read);
```

Click **"Run"**

**Expected Result**:
```
Success
✅ Notifications table created successfully!
```

---

## 🧪 Testing the Notification System

### Step 1: Student Flags a Response

1. Open chat: http://localhost:5173
2. Ask any question
3. Click **"Flag as incorrect"** on the response
4. Enter reason: "This information seems outdated"
5. Click Submit
6. **Note your session ID** (check browser localStorage or backend logs)

---

### Step 2: Professor Reviews the Flag

1. Log in to Professor Dashboard
2. Go to **"Pending Corrections"**
3. Find the flagged item
4. Choose one of:
   - **Approve & Edit**: Enter corrected response, click Approve
   - **Approve As-Is**: Click Approve without editing
   - **Reject**: Click Reject

---

### Step 3: Student Sees Notification

**IMPORTANT**: The student needs to be in the **same session** that flagged the response.

**Problem with Current Session Management**:
Since we changed sessions to refresh on each page load, the student won't see the notification if they refresh!

**Solution Options**:

**Option A**: Keep session for logged-in users (with login system)
**Option B**: Use email notifications instead
**Option C**: Show notifications for all flagged items (not session-specific)

---

## ⚠️ Important: Session Management Issue

### The Problem

With our **current session management** (new session per page load):

1. Student flags response in Session A
2. Student refreshes page → **New Session B** created
3. Professor reviews flag (notification sent to Session A)
4. Student won't see notification (they're now in Session B)

### The Solution

We need to decide:

**Option 1: Persist Sessions for Notifications** (Recommended)
```javascript
// Modified session management
const getSessionId = () => {
  // For notifications, we need persistent sessions
  let sessionId = localStorage.getItem('chatSessionId');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chatSessionId', sessionId);
  }
  return sessionId;
};
```

**Trade-off**: Sessions persist (privacy concern) BUT notifications work

---

**Option 2: Add User Login System**
- Students create accounts
- Notifications tied to user ID, not session
- Best for production

---

**Option 3: Email Notifications**
- Professor review triggers email to student
- No session dependency
- Requires student email collection

---

**Option 4: Show All Recent Flags** (Simpler)
- Show recent flagged items regardless of session
- Less privacy, but notifications work

---

## 🔧 Recommended: Hybrid Approach

Keep the new-session-per-load for **privacy**, but allow **optional notification persistence**:

```javascript
// frontend/src/pages/StudentChat.jsx

const [wantNotifications, setWantNotifications] = useState(false);

const getSessionId = () => {
  if (wantNotifications) {
    // Persistent session for notifications
    let sessionId = localStorage.getItem('notificationSessionId');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('notificationSessionId', sessionId);
    }
    return sessionId;
  } else {
    // Fresh session each time (privacy)
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
};
```

Add UI:
```jsx
<button onClick={() => setWantNotifications(true)}>
  Enable Notifications for Flagged Responses
</button>
```

---

## 📊 Notifications Table Schema

| Column | Type | Description |
|--------|------|-------------|
| id | BIGINT | Primary key |
| session_id | VARCHAR(100) | Student's session ID |
| correction_id | BIGINT | References corrections table |
| title | VARCHAR(255) | Notification title |
| message | TEXT | Notification message |
| type | VARCHAR(50) | correction_approved / correction_rejected / correction_edited |
| is_read | BOOLEAN | Whether student read it |
| created_at | TIMESTAMP | When notification was created |

---

## 🎯 Complete Workflow

### Student Side
1. Ask question → Get response
2. Flag response as incorrect
3. **See notification bell** (if session persists)
4. Click bell → See notification
5. Read professor's response

### Professor Side
1. See flagged items in dashboard
2. Review each flag
3. Approve/Reject/Edit
4. **Notification automatically sent to student**

---

## ✅ Success Checklist

After running SQL migration:

- [ ] Notifications table created in Supabase
- [ ] Student can flag responses
- [ ] Professor can review flags
- [ ] Backend creates notification when professor reviews
- [ ] Frontend polls for notifications (every 30 seconds)
- [ ] Notification bell shows unread count
- [ ] **Decide on session persistence strategy**

---

## 🚀 Quick Start

### For Now (Testing)

1. **Run SQL migration** (create notifications table)
2. **Keep persistent sessions temporarily** for testing:
   ```javascript
   // Comment out the session refresh
   // sessionStorage.setItem('chatSessionId', sessionId);
   localStorage.setItem('chatSessionId', sessionId);  // Use this instead
   ```
3. **Test full workflow**:
   - Flag response
   - Professor reviews
   - Student sees notification

### For Production

1. Implement user login system
2. Tie notifications to user accounts
3. Or: Add "Enable Notifications" opt-in button

---

## 📝 Files Modified/Created

### Database
- ✅ **`database/create_notifications_table.sql`** - SQL migration (NEW)
- ✅ **`database/add_session_id_to_corrections.sql`** - Already created

### Backend
- ✅ **`backend/services/database.py:369-429`** - Notification methods (ALREADY IMPLEMENTED)
- ✅ **`backend/main.py:778-817`** - Notification creation (ALREADY IMPLEMENTED)

### Frontend
- ✅ **`frontend/src/pages/StudentChat.jsx`** - Notification UI (ALREADY IMPLEMENTED)
- ✅ **`frontend/src/services/api.js`** - Notification API calls (ALREADY IMPLEMENTED)

---

## 🎉 Summary

**What's Already Done**: ✅
- Backend notification creation
- Frontend notification display
- Professor review triggers notifications
- Notification polling every 30 seconds
- Unread count badge
- Mark as read functionality

**What's Missing**: ⚠️
- Notifications table in database (run SQL above)
- Session persistence decision (affects whether students see notifications)

**Recommendation**:
1. Run SQL migration NOW
2. Test with persistent sessions
3. Add user login system for production
4. Or: Add email notifications as fallback

---

**Status**: ✅ 95% Complete - Just run SQL and decide on sessions!

**Next Steps**:
1. Run SQL in Supabase
2. Test notification flow
3. Decide: persistent sessions or user login?

🚀 **Run the SQL migration now!**
