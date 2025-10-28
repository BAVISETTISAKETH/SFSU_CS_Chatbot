# ⚡ Quick Setup: Professor Review Notifications

**Goal**: When professor reviews a flagged response, student gets notified
**Status**: ✅ Code already done - Just needs database + one decision
**Time**: 2 minutes

---

## 🚀 Step 1: Create Notifications Table (30 seconds)

### In Supabase SQL Editor:

```sql
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    correction_id BIGINT REFERENCES corrections(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX notifications_session_id_idx ON notifications(session_id);
CREATE INDEX notifications_is_read_idx ON notifications(is_read);
```

Click **Run** ✅

---

## ⚠️ Step 2: Fix Session Persistence Issue

### The Problem

We changed sessions to **refresh on every page load** for privacy.

**But this breaks notifications!**

**Why**:
1. Student flags response in Session A
2. Student refreshes page → **New Session B**
3. Professor reviews (notification sent to Session A)
4. Student in Session B **can't see notification** ❌

---

## ✅ Step 3: Choose Solution

### Option 1: Keep Persistent Sessions (Quick Fix for Testing)

**Do this NOW for testing**:

```javascript
// frontend/src/pages/StudentChat.jsx:15-21

// CHANGE THIS:
const getSessionId = () => {
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  sessionStorage.setItem('chatSessionId', sessionId);  // <- Uses sessionStorage
  return sessionId;
};

// TO THIS:
const getSessionId = () => {
  let sessionId = localStorage.getItem('chatSessionId');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chatSessionId', sessionId);  // <- Uses localStorage
  }
  return sessionId;
};
```

**Also change line 111**:

```javascript
// CHANGE THIS:
// useEffect(() => {
//   localStorage.setItem(`chatMessages_${sessionId}`, JSON.stringify(messages));
// }, [messages, sessionId]);

// TO THIS (uncomment):
useEffect(() => {
  localStorage.setItem(`chatMessages_${sessionId}`, JSON.stringify(messages));
}, [messages, sessionId]);
```

**Trade-off**: Sessions persist (students see old chats) BUT notifications work ✅

---

### Option 2: Production Solution (Later)

For production, add:
- User login system
- Notifications tied to user ID (not session)
- Or: Email notifications

**For now**: Use Option 1 to test notifications!

---

## 🧪 Testing

### Step 1: Student Side

1. Open chat: http://localhost:5173
2. Ask: "What is CS 101?"
3. Click **"Flag as incorrect"**
4. Enter reason: "Testing notifications"
5. Click Submit
6. **DON'T REFRESH** (stay in same session)

---

### Step 2: Professor Side

1. Go to Professor Dashboard
2. Find flagged item in "Pending Corrections"
3. Review and **Approve** or **Reject**

---

### Step 3: Student Sees Notification

1. In the student chat (same tab from Step 1)
2. Wait 30 seconds (or refresh manually)
3. **See notification bell** with badge 🔔 **1**
4. Click bell → See professor's response

**If you see the notification** → ✅ Working!

---

## 📊 How It Works

### When Professor Reviews:

**Approves with Corrections**:
```
Student sees:
┌──────────────────────────┐
│ 🔔 Response Corrected ✅ │
│ A professor has reviewed │
│ and corrected the        │
│ response to: "What is... │
└──────────────────────────┘
```

**Approves As-Is**:
```
Student sees:
┌──────────────────────────┐
│ 🔔 Response Verified ✅  │
│ A professor has verified │
│ the response to: "What...│
└──────────────────────────┘
```

**Rejects Flag**:
```
Student sees:
┌──────────────────────────┐
│ 🔔 Flag Reviewed ℹ️      │
│ A professor has reviewed │
│ your flag. The original  │
│ response was correct.    │
└──────────────────────────┘
```

---

## ✅ Quick Checklist

- [ ] Run SQL in Supabase (create notifications table)
- [ ] Change `sessionStorage` → `localStorage` in StudentChat.jsx
- [ ] Uncomment message persistence useEffect
- [ ] Restart frontend
- [ ] Test: Flag response → Professor reviews → Student sees notification

---

## 🎯 What's Already Implemented

**Backend** (`backend/main.py:778-817`):
- ✅ Creates notification when professor reviews
- ✅ Different messages for approve/reject/edit
- ✅ Tied to student's session_id

**Frontend** (`frontend/src/pages/StudentChat.jsx`):
- ✅ Notification bell icon in header
- ✅ Polls for notifications every 30 seconds
- ✅ Shows unread count badge
- ✅ Mark as read functionality
- ✅ Displays notification list

**Database Service** (`backend/services/database.py`):
- ✅ create_notification() method
- ✅ get_notifications() method
- ✅ mark_notification_as_read() method

---

## 🚀 TL;DR

**3 steps**:

1. **Supabase**: Run SQL to create notifications table
2. **Frontend**: Change `sessionStorage` → `localStorage` (2 places)
3. **Test**: Flag → Professor reviews → Student sees notification

**Time**: 2 minutes
**Result**: Working notification system! 🎉

---

**For detailed info**: See `NOTIFICATION_SYSTEM_GUIDE.md`

**Run SQL now and make the code changes!** ⚡
