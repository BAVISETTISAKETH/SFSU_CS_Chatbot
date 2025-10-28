# Complete Notification System Implementation Guide

## Overview
This guide will help you complete the notification system that allows students to flag incorrect responses and receive notifications when professors review them.

---

## Step 1: Setup Database Schema

1. **Run the setup script**:
   ```bash
   python setup_notifications.py
   ```

2. **Copy the SQL commands** shown in the output

3. **Execute in Supabase**:
   - Go to your Supabase Dashboard: https://supabase.com/dashboard
   - Navigate to "SQL Editor"
   - Create a new query
   - Paste the SQL commands from step 2
   - Click "Run"

The SQL will create:
- `notifications` table for storing student notifications
- Add `session_id` column to `corrections` table
- Create necessary indexes for performance
- Create helper function for querying notifications

---

## Step 2: Update Frontend API Client

Update `frontend/src/services/api.js` to pass `session_id` when flagging:

```javascript
// Update the flagIncorrect function
export const flagIncorrect = async (query, response, reason, sessionId) => {
  const res = await api.post('/corrections/flag', {
    query,
    response,
    reason,
    session_id: sessionId  // <-- Add this
  });
  return res.data;
};

// Add notification functions
export const getNotifications = async (sessionId) => {
  const response = await api.get(`/notifications/${sessionId}`);
  return response.data;
};

export const markNotificationAsRead = async (notificationId) => {
  const response = await api.post(`/notifications/${notificationId}/mark-read`);
  return response.data;
};

export const markAllNotificationsAsRead = async (sessionId) => {
  const response = await api.post(`/notifications/${sessionId}/mark-all-read`);
  return response.data;
};
```

---

## Step 3: Update StudentChat to Pass Session ID

In `frontend/src/pages/StudentChat.jsx`, update the `submitFlag` function (around line 160):

```javascript
const submitFlag = async () => {
  if (!flagReason.trim()) return;

  try {
    const userQuery = messages[messages.indexOf(flaggedMessage) - 1]?.content || '';
    // Pass sessionId to flagIncorrect
    await flagIncorrect(userQuery, flaggedMessage.content, flagReason, sessionId);
    alert('Thank you! A professor will review this response. You\'ll be notified when it\'s reviewed.');
    setShowFlagDialog(false);
    setFlagReason('');
    setFlaggedMessage(null);
  } catch (error) {
    alert('Failed to submit flag. Please try again.');
  }
};
```

---

## Step 4: Add Notifications Display to StudentChat

1. **Add notification state** (around line 54):

```javascript
import { Bell } from 'lucide-react';  // Add Bell icon to imports
const [notifications, setNotifications] = useState([]);
const [unreadCount, setUnreadCount] = useState(0);
const [showNotifications, setShowNotifications] = useState(false);
```

2. **Add function to fetch notifications**:

```javascript
const loadNotifications = async () => {
  try {
    const data = await getNotifications(sessionId);
    setNotifications(data.notifications);
    setUnreadCount(data.unread_count);
  } catch (error) {
    console.error('Failed to load notifications:', error);
  }
};

// Poll for notifications every 30 seconds
useEffect(() => {
  loadNotifications();
  const interval = setInterval(loadNotifications, 30000);
  return () => clearInterval(interval);
}, [sessionId]);
```

3. **Add notification bell button** in the header (after Export button, around line 323):

```javascript
<motion.button
  onClick={() => setShowNotifications(!showNotifications)}
  className="glass px-3 md:px-4 py-2 rounded-xl text-white transition-all duration-300 flex items-center gap-2 relative"
  whileHover={{ scale: 1.05, y: -2 }}
  whileTap={{ scale: 0.95 }}
  title="Notifications"
>
  <Bell className="w-4 h-4" />
  {unreadCount > 0 && (
    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
      {unreadCount}
    </span>
  )}
  <span className="hidden md:inline">Notifications</span>
</motion.button>
```

4. **Add notification panel** (before the Flag Dialog, around line 790):

```javascript
{/* Notifications Panel */}
<AnimatePresence>
  {showNotifications && (
    <motion.div
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={() => setShowNotifications(false)}
    >
      <motion.div
        className="glass-strong rounded-2xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-layers-purple"
        initial={{ scale: 0.8, y: 50 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.8, y: 50 }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold gradient-shine">Notifications</h3>
          {notifications.length > 0 && (
            <button
              onClick={async () => {
                await markAllNotificationsAsRead(sessionId);
                await loadNotifications();
              }}
              className="text-sm text-purple-400 hover:text-purple-300"
            >
              Mark all as read
            </button>
          )}
        </div>

        {notifications.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <Bell className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No notifications yet</p>
            <p className="text-sm mt-2">You'll be notified when professors review your flags</p>
          </div>
        ) : (
          <div className="space-y-4">
            {notifications.map((notification) => (
              <motion.div
                key={notification.id}
                className={`p-4 rounded-xl ${
                  notification.is_read ? 'glass-card' : 'glass-strong border-2 border-purple-500/50'
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-bold text-white mb-1">{notification.title}</h4>
                    <p className="text-sm text-gray-300 mb-2">{notification.message}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                  {!notification.is_read && (
                    <button
                      onClick={async () => {
                        await markNotificationAsRead(notification.id);
                        await loadNotifications();
                      }}
                      className="text-xs text-purple-400 hover:text-purple-300 ml-4"
                    >
                      Mark read
                    </button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        <div className="mt-6">
          <motion.button
            onClick={() => setShowNotifications(false)}
            className="w-full px-6 py-3 glass rounded-xl text-white"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Close
          </button>
        </div>
      </motion.div>
    </motion.div>
  )}
</AnimatePresence>
```

---

## Step 5: Test the Complete Workflow

### Test as Student:
1. Start the backend: `cd backend && ../venv/Scripts/python.exe main.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Open the chat at `http://localhost:5173/chat`
4. Ask a question
5. Click "Flag as incorrect" on the response
6. Enter a reason and submit
7. You should see: "Thank you! A professor will review this response. You'll be notified when it's reviewed."

### Test as Professor:
1. Login as professor at `http://localhost:5173/professor`
2. Go to "Pending Corrections" tab
3. You should see the flagged response
4. Click "Approve", "Correct" (with edits), or "Reject"
5. The correction should be processed

### Verify Notifications:
1. Go back to the student chat (same session)
2. Click the bell icon in the header
3. You should see a notification from the professor
4. The notification shows what action the professor took

---

## How It Works

### Workflow Diagram:

```
Student flags response
        ↓
Flag stored in database with session_id
        ↓
Professor reviews flag in dashboard
        ↓
Professor approves/edits/rejects
        ↓
Notification created with session_id
        ↓
Student sees notification in chat
```

### Data Flow:

1. **Student Side**:
   - SessionID is generated on first visit and stored in localStorage
   - When flagging, sessionID is sent to backend
   - Notifications are polled every 30 seconds
   - Bell icon shows unread count

2. **Backend**:
   - Flag creates correction record with session_id
   - Professor review creates notification with same session_id
   - Notifications API returns notifications for a session

3. **Professor Side**:
   - Sees pending corrections
   - Reviews and takes action
   - Backend automatically creates notifications

---

## Troubleshooting

### "Flag has not been sent" error:
- Check browser console for errors
- Verify backend is running on port 8000
- Check that session_id column exists in corrections table
- Verify notifications table exists

### Notifications not appearing:
- Check that session_id was stored with the correction
- Verify notification was created in database
- Check browser console for API errors
- Ensure frontend is polling notifications

### Database errors:
- Run the setup_notifications.py script
- Execute all SQL commands in Supabase
- Check Supabase logs for errors
- Verify table permissions

---

## Next Steps

After completing this implementation, you can enhance it with:

1. **Real-time notifications** using Supabase Realtime subscriptions
2. **Email notifications** when professors review flags
3. **Push notifications** for mobile users
4. **Notification preferences** for students
5. **Notification history** page

---

## Questions?

If you encounter issues:
1. Check browser console (F12)
2. Check backend logs
3. Verify all SQL commands executed successfully
4. Test each step individually

The system is now fully implemented and ready to test!
