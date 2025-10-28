import { useState, useRef, useEffect } from 'react';
import { Send, Flag, Bot, User, Sparkles, Home, Download, Copy, Check, Zap, BookOpen, GraduationCap, DollarSign, Globe, Building, ThumbsUp, ThumbsDown, Plus, Bell, Eye } from 'lucide-react';
import { chat, flagIncorrect, submitFeedback, getNotifications, markNotificationAsRead, markAllNotificationsAsRead, getCorrectionDetails } from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import LiquidGlassBackground from '../components/LiquidGlassBackground';
import AlliGatorIcon from '../components/AlliGatorIcon';

export default function StudentChat() {
  const navigate = useNavigate();

  // Generate or retrieve persistent session ID (needed for notifications)
  const getSessionId = () => {
    // Use persistent session so students can receive notifications from professors
    let sessionId = localStorage.getItem('chatSessionId');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('chatSessionId', sessionId);
    }
    return sessionId;
  };

  const [sessionId] = useState(getSessionId());

  // Load messages from localStorage for persistent chat history
  const loadMessages = (sid) => {
    const savedMessages = localStorage.getItem(`chatMessages_${sid}`);
    if (savedMessages) {
      try {
        return JSON.parse(savedMessages);
      } catch (e) {
        console.error('Failed to parse saved messages:', e);
      }
    }
    return [
      {
        role: 'assistant',
        content: 'Hello! I\'m **Alli**, your intelligent Gator Guide for SFSU! 🎓\n\nI can help you with:\n• Course requirements & descriptions\n• Faculty information\n• Financial aid & scholarships\n• International student services\n• Housing & campus resources\n\nWhat would you like to know?',
      },
    ];
  };

  const [messages, setMessages] = useState(loadMessages(sessionId));
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showFlagDialog, setShowFlagDialog] = useState(false);
  const [flaggedMessage, setFlaggedMessage] = useState(null);
  const [flagReason, setFlagReason] = useState('');
  const [copiedId, setCopiedId] = useState(null);
  const [showWelcome, setShowWelcome] = useState(true);
  const [feedbackGiven, setFeedbackGiven] = useState({}); // Track feedback per message
  const [suggestedQuestions, setSuggestedQuestions] = useState([]); // Smart suggestions
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [viewingCorrection, setViewingCorrection] = useState(null);
  const [correctionDetails, setCorrectionDetails] = useState(null);
  const messagesEndRef = useRef(null);

  // Enhanced quick question categories
  const quickQuestionCategories = [
    {
      icon: GraduationCap,
      title: "Courses",
      color: "#3b82f6",
      questions: [
        "What CS courses are required for graduation?",
        "Tell me about CS 665",
        "What are the prerequisites for CS 673?"
      ]
    },
    {
      icon: DollarSign,
      title: "Financial Aid",
      color: "#10b981",
      questions: [
        "How do I apply for financial aid?",
        "What scholarships are available?",
        "Tell me about FAFSA deadlines"
      ]
    },
    {
      icon: Globe,
      title: "International",
      color: "#8b5cf6",
      questions: [
        "What is CPT and OPT?",
        "How do I get a student visa?",
        "International student resources"
      ]
    },
    {
      icon: Building,
      title: "Campus Life",
      color: "#f59e0b",
      questions: [
        "Tell me about on-campus housing",
        "What student services are available?",
        "Campus recreation facilities"
      ]
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadNotifications = async () => {
    try {
      const data = await getNotifications(sessionId);
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const viewCorrectionDetails = async (correctionId) => {
    try {
      const details = await getCorrectionDetails(correctionId);
      setCorrectionDetails(details);
      setViewingCorrection(correctionId);
    } catch (error) {
      console.error('Failed to load correction details:', error);
      alert('Failed to load correction details. Please try again.');
    }
  };

  // Save messages to localStorage whenever they change - SESSION SPECIFIC
  useEffect(() => {
    localStorage.setItem(`chatMessages_${sessionId}`, JSON.stringify(messages));
  }, [messages, sessionId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load notifications on mount and poll every 30 seconds
  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 30000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setShowWelcome(false);
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Send last 6 messages (3 exchanges) for context - like ChatGPT
      const history = messages
        .slice(1)  // Skip welcome message
        .slice(-6) // Last 3 exchanges
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));

      const response = await chat(userMessage, history, sessionId);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response, id: Date.now() },
      ]);

      // Update suggested questions if provided
      if (response.suggested_questions && response.suggested_questions.length > 0) {
        setSuggestedQuestions(response.suggested_questions);
      }
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFlag = (message) => {
    setFlaggedMessage(message);
    setShowFlagDialog(true);
  };

  const submitFlag = async () => {
    if (!flagReason.trim()) return;

    try {
      const userQuery = messages[messages.indexOf(flaggedMessage) - 1]?.content || '';
      await flagIncorrect(userQuery, flaggedMessage.content, flagReason, sessionId);
      alert('Thank you! A professor will review this response. You\'ll be notified when it\'s reviewed.');
      setShowFlagDialog(false);
      setFlagReason('');
      setFlaggedMessage(null);
    } catch (error) {
      console.error('Flag submission error:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to submit flag: ${error.response?.data?.detail || error.message}`);
    }
  };

  const copyMessage = (content, id) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleFeedback = async (message, index, feedbackType) => {
    const messageId = message.id || index;

    // Don't allow changing feedback once given
    if (feedbackGiven[messageId]) return;

    try {
      const userQuery = messages[index - 1]?.content || '';
      await submitFeedback(userQuery, message.content, feedbackType, sessionId, String(messageId));

      // Mark feedback as given for this message
      setFeedbackGiven(prev => ({
        ...prev,
        [messageId]: feedbackType
      }));
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const startNewChat = () => {
    // Clear current session and create a new one
    localStorage.removeItem(`chatMessages_${sessionId}`);
    localStorage.removeItem('chatSessionId');

    // Reset states
    setFeedbackGiven({});
    setShowWelcome(true);
    setSuggestedQuestions([]);

    // Reload page to get fresh session
    window.location.reload();
  };

  const exportChat = () => {
    const chatText = messages.map(msg => `${msg.role === 'user' ? 'You' : 'Alli'}: ${msg.content}`).join('\n\n');
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sfsu-chat-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const askQuickQuestion = (question) => {
    setInput(question);
    setShowWelcome(false);
  };

  return (
    <div className="flex flex-col h-screen relative overflow-hidden bg-slate-950">
      {/* Animated Background - DARK MODE */}
      <motion.div
        className="absolute inset-0 animate-gradient"
        style={{
          background: 'linear-gradient(135deg, #000000 0%, #0a0a0a 20%, #1a1a1a 40%, #0f0f0f 60%, #050505 80%, #000000 100%)',
          backgroundSize: '400% 400%'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      ></motion.div>

      {/* Apple-Style Liquid Glass Background */}
      <LiquidGlassBackground />

      {/* Enhanced Header */}
      <motion.header
        className="relative z-10 glass-dark border-b border-white/10"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-6xl mx-auto px-4 md:px-6 py-3 md:py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 md:gap-4">
            <motion.button
              onClick={() => navigate('/')}
              className="glass px-3 md:px-4 py-2 rounded-xl text-white transition-all duration-300 flex items-center gap-2"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Home</span>
            </motion.button>
            <div className="flex items-center gap-3">
              <motion.div
                className="w-10 h-10 md:w-12 md:h-12 rounded-2xl flex items-center justify-center shadow-layers-purple"
                style={{ background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)' }}
                animate={{
                  boxShadow: [
                    "0 0 20px rgba(75, 46, 131, 0.5)",
                    "0 0 40px rgba(180, 151, 90, 0.6)",
                    "0 0 20px rgba(75, 46, 131, 0.5)"
                  ]
                }}
                transition={{ duration: 2, repeat: Infinity }}
                whileHover={{ rotate: 360, scale: 1.1 }}
              >
                <AlliGatorIcon className="w-6 h-6 md:w-8 md:h-8" />
              </motion.div>
              <div>
                <h1 className="text-lg md:text-2xl font-bold gradient-shine flex items-center gap-2">
                  Alli - Your Gator Guide
                </h1>
                <p className="text-xs md:text-sm hidden md:block" style={{color: '#DCC890'}}>
                  <Zap className="w-3 h-3 inline mr-1" />
                  Powered by Groq AI + RAG
                </p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 md:gap-3">
            <motion.button
              onClick={startNewChat}
              className="glass px-3 md:px-4 py-2 rounded-xl text-white transition-all duration-300 flex items-center gap-2"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              title="Start New Chat"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden md:inline">New Chat</span>
            </motion.button>
            <motion.button
              onClick={exportChat}
              className="glass px-3 md:px-4 py-2 rounded-xl text-white transition-all duration-300 flex items-center gap-2"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              title="Export Chat"
            >
              <Download className="w-4 h-4" />
              <span className="hidden md:inline">Export</span>
            </motion.button>
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
            <motion.a
              href="/professor"
              className="glass px-3 md:px-6 py-2 md:py-2.5 rounded-xl text-white text-sm md:text-base font-medium transition-all duration-300 shadow-layers-purple"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
              whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
              whileTap={{ scale: 0.95 }}
            >
              <span className="hidden sm:inline">Professor Login</span>
              <span className="sm:hidden">Login</span>
            </motion.a>
          </div>
        </div>
      </motion.header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 relative z-10">
        <div className="max-w-4xl mx-auto space-y-6">

          {/* Welcome Screen - Enhanced */}
          <AnimatePresence>
            {showWelcome && messages.length === 1 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                {/* Welcome Banner with Liquid Glass */}
                <motion.div
                  className="liquid-panel rounded-3xl p-8 text-center shadow-layers-purple liquid-shimmer"
                  initial={{ scale: 0.9 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200 }}
                >
                  <motion.div
                    className="inline-block"
                    animate={{
                      rotate: [0, 10, -10, 10, 0],
                      scale: [1, 1.1, 1]
                    }}
                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                  >
                    <Bot className="w-16 h-16 mx-auto mb-4" style={{color: '#B4975A'}} />
                  </motion.div>
                  <h2 className="text-3xl font-bold gradient-shine mb-3">Welcome to Gator Guide!</h2>
                  <p className="text-gray-300 max-w-2xl mx-auto">
                    I'm Alli, your AI-powered assistant for all things SFSU. Ask me anything about courses,
                    financial aid, housing, international services, and more!
                  </p>
                </motion.div>

                {/* Quick Question Categories */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {quickQuestionCategories.map((category, idx) => (
                    <motion.div
                      key={idx}
                      className="liquid-card rounded-2xl p-6 tilt-card"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <div className="flex items-center gap-3 mb-4">
                        <motion.div
                          className="w-12 h-12 rounded-xl flex items-center justify-center"
                          style={{
                            background: `linear-gradient(135deg, ${category.color} 0%, ${category.color}dd 100%)`
                          }}
                          whileHover={{ rotate: 360 }}
                          transition={{ duration: 0.6 }}
                        >
                          <category.icon className="w-6 h-6 text-white" />
                        </motion.div>
                        <h3 className="text-lg font-bold text-white">{category.title}</h3>
                      </div>
                      <div className="space-y-2">
                        {category.questions.map((question, qIdx) => (
                          <motion.button
                            key={qIdx}
                            onClick={() => askQuickQuestion(question)}
                            className="w-full text-left px-4 py-2 rounded-lg glass text-sm text-gray-200 hover:text-white transition-all duration-300"
                            whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.1)' }}
                            whileTap={{ scale: 0.98 }}
                          >
                            • {question}
                          </motion.button>
                        ))}
                      </div>
                    </motion.div>
                  ))}
                </div>

                {/* Features Banner */}
                <motion.div
                  className="grid grid-cols-3 gap-4 glass-card rounded-2xl p-6"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  <div className="text-center">
                    <Zap className="w-8 h-8 mx-auto mb-2" style={{color: '#f59e0b'}} />
                    <p className="text-sm text-gray-300">Instant Answers</p>
                  </div>
                  <div className="text-center">
                    <BookOpen className="w-8 h-8 mx-auto mb-2" style={{color: '#3b82f6'}} />
                    <p className="text-sm text-gray-300">RAG-Powered</p>
                  </div>
                  <div className="text-center">
                    <Sparkles className="w-8 h-8 mx-auto mb-2" style={{color: '#8b5cf6'}} />
                    <p className="text-sm text-gray-300">AI Assistant</p>
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Messages */}
          <AnimatePresence mode="popLayout">
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{
                duration: 0.4,
                type: "spring",
                stiffness: 300,
                damping: 30
              }}
              layout
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`flex gap-4 max-w-3xl ${
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                {/* Avatar with Interactive Motion */}
                <motion.div
                  className={`flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center ${
                    message.role === 'user'
                      ? 'shadow-layers-gold'
                      : 'shadow-layers-purple'
                  }`}
                  style={{
                    background: message.role === 'user'
                      ? 'linear-gradient(135deg, #B4975A 0%, #C9AD74 100%)'
                      : 'linear-gradient(135deg, #4B2E83 0%, #6B4FA3 100%)'
                  }}
                  whileHover={{ scale: 1.1, rotate: 360 }}
                  transition={{ duration: 0.5 }}
                  animate={message.role === 'assistant' ? {
                    boxShadow: [
                      "0 0 10px rgba(75, 46, 131, 0.5)",
                      "0 0 20px rgba(75, 46, 131, 0.8)",
                      "0 0 10px rgba(75, 46, 131, 0.5)"
                    ]
                  } : {}}
                >
                  {message.role === 'user' ? (
                    <User className="w-6 h-6 text-white" />
                  ) : (
                    <Bot className="w-6 h-6 text-white" />
                  )}
                </motion.div>

                {/* Message */}
                <div className="flex-1">
                  <motion.div
                    className={`message-bubble px-6 py-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'text-white shadow-layers-gold'
                        : message.error
                        ? 'glass-card border-red-500/30 text-red-200'
                        : 'glass-card text-white shadow-layers'
                    }`}
                    style={message.role === 'user' ? {
                      background: 'linear-gradient(135deg, #B4975A 0%, #C9AD74 100%)'
                    } : {}}
                    whileHover={{ y: -2 }}
                  >
                    {message.role === 'assistant' ? (
                      <div className="prose prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    )}
                  </motion.div>

                  {/* Action buttons for Assistant Messages */}
                  {message.role === 'assistant' && !message.error && (
                    <motion.div
                      className="flex items-center gap-4 mt-2 ml-2"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      {/* Thumbs Up/Down Feedback */}
                      <motion.button
                        onClick={() => handleFeedback(message, index, 'thumbs_up')}
                        className={`text-xs flex items-center gap-1.5 transition-all duration-300 ${
                          feedbackGiven[message.id || index] === 'thumbs_up'
                            ? 'text-green-400'
                            : 'text-gray-400 hover:text-green-400'
                        }`}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={feedbackGiven[message.id || index]}
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        {feedbackGiven[message.id || index] === 'thumbs_up' && 'Helpful'}
                      </motion.button>

                      <motion.button
                        onClick={() => handleFeedback(message, index, 'thumbs_down')}
                        className={`text-xs flex items-center gap-1.5 transition-all duration-300 ${
                          feedbackGiven[message.id || index] === 'thumbs_down'
                            ? 'text-red-400'
                            : 'text-gray-400 hover:text-red-400'
                        }`}
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        disabled={feedbackGiven[message.id || index]}
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                        {feedbackGiven[message.id || index] === 'thumbs_down' && 'Not helpful'}
                      </motion.button>

                      <motion.button
                        onClick={() => copyMessage(message.content, message.id || index)}
                        className="text-xs text-gray-400 hover:text-purple-400 flex items-center gap-1.5 transition-all duration-300"
                        whileHover={{ scale: 1.05, x: 2 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        {copiedId === (message.id || index) ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            Copy
                          </>
                        )}
                      </motion.button>
                      <motion.button
                        onClick={() => handleFlag(message)}
                        className="text-xs text-gray-400 hover:text-red-400 flex items-center gap-1.5 transition-all duration-300"
                        whileHover={{ scale: 1.05, x: 2 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Flag className="w-3.5 h-3.5" />
                        Flag as incorrect
                      </motion.button>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
          </AnimatePresence>

          {/* Enhanced Loading Indicator */}
          <AnimatePresence>
            {loading && (
              <motion.div
                className="flex justify-start"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <div className="flex gap-4 max-w-3xl">
                  <motion.div
                    className="flex-shrink-0 w-12 h-12 rounded-2xl flex items-center justify-center shadow-layers-purple"
                    style={{background: 'linear-gradient(135deg, #4B2E83 0%, #6B4FA3 100%)'}}
                    animate={{
                      boxShadow: [
                        "0 0 10px rgba(75, 46, 131, 0.5)",
                        "0 0 20px rgba(75, 46, 131, 0.8)",
                        "0 0 10px rgba(75, 46, 131, 0.5)"
                      ]
                    }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <Bot className="w-6 h-6 text-white" />
                  </motion.div>
                  <div className="glass-card px-6 py-4 rounded-2xl">
                    <div className="flex gap-2">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-2.5 h-2.5 rounded-full"
                          style={{background: '#6B4FA3'}}
                          animate={{
                            y: [0, -10, 0],
                            scale: [1, 1.2, 1]
                          }}
                          transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            delay: i * 0.1
                          }}
                        ></motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={messagesEndRef} />

          {/* Smart Suggestions - People Also Asked */}
          <AnimatePresence>
            {suggestedQuestions.length > 0 && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
                className="mt-6"
              >
                <motion.div
                  className="glass-card rounded-2xl p-6"
                  whileHover={{ scale: 1.01 }}
                >
                  <h3 className="text-lg font-bold gradient-shine mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5" style={{color: '#B4975A'}} />
                    People also asked
                  </h3>
                  <div className="space-y-2">
                    {suggestedQuestions.map((question, idx) => (
                      <motion.button
                        key={idx}
                        onClick={() => {
                          setInput(question);
                          setSuggestedQuestions([]);
                        }}
                        className="w-full text-left px-4 py-3 rounded-xl glass text-sm text-gray-200 hover:text-white transition-all duration-300 flex items-center gap-2"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        whileHover={{ x: 5, backgroundColor: 'rgba(255,255,255,0.1)' }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <span className="text-gray-400">→</span>
                        {question}
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Enhanced Input Area */}
      <motion.div
        className="relative z-10 glass-dark border-t border-white/10 p-4 md:p-6"
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2 md:gap-3">
            <motion.input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about courses, faculty, financial aid, housing..."
              className="flex-1 px-6 py-4 glass-card text-white placeholder-gray-400 rounded-2xl focus:outline-none input-glow transition-all duration-300"
              disabled={loading}
              whileFocus={{ scale: 1.01 }}
              transition={{ type: "spring", stiffness: 300 }}
            />
            <motion.button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="text-white px-6 md:px-8 py-4 rounded-2xl btn-ripple liquid-btn transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-layers-purple"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
              whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
              whileTap={{ scale: 0.95 }}
              animate={!input.trim() ? {} : {
                boxShadow: [
                  "0 0 10px rgba(75, 46, 131, 0.4)",
                  "0 0 20px rgba(180, 151, 90, 0.6)",
                  "0 0 10px rgba(75, 46, 131, 0.4)"
                ]
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Send className="w-5 h-5" />
              <span className="hidden md:inline">Send</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

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
                          {notification.correction_id && (
                            <button
                              onClick={() => viewCorrectionDetails(notification.correction_id)}
                              className="mt-2 px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded-lg text-xs text-white flex items-center gap-1"
                            >
                              <Eye className="w-3 h-3" />
                              View Response
                            </button>
                          )}
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
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Correction Details Modal */}
      <AnimatePresence>
        {viewingCorrection && correctionDetails && (
          <motion.div
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => {
              setViewingCorrection(null);
              setCorrectionDetails(null);
            }}
          >
            <motion.div
              className="glass-strong rounded-2xl p-8 max-w-3xl w-full max-h-[85vh] overflow-y-auto shadow-layers-purple"
              initial={{ scale: 0.8, y: 50 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.8, y: 50 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold mb-6 gradient-shine">Professor's Response</h3>

              {/* Original Question */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-purple-400 mb-2">Your Question:</h4>
                <div className="glass-card p-4 rounded-xl">
                  <p className="text-white">{correctionDetails.student_query}</p>
                </div>
              </div>

              {/* Original Response */}
              <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Original Response:</h4>
                <div className="glass-card p-4 rounded-xl border border-gray-500/30">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    className="prose prose-invert prose-sm max-w-none"
                  >
                    {correctionDetails.original_response}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Corrected Response or Status */}
              {correctionDetails.corrected_response ? (
                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-green-400 mb-2 flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    Professor's Corrected Response:
                  </h4>
                  <div className="glass-card p-4 rounded-xl border-2 border-green-500/50 bg-green-500/5">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      className="prose prose-invert prose-sm max-w-none"
                    >
                      {correctionDetails.corrected_response}
                    </ReactMarkdown>
                  </div>
                </div>
              ) : correctionDetails.status === 'approved' ? (
                <div className="mb-6">
                  <div className="glass-card p-4 rounded-xl border-2 border-blue-500/50 bg-blue-500/5">
                    <p className="text-blue-300 flex items-center gap-2">
                      <Check className="w-4 h-4" />
                      The professor verified that the original response was correct.
                    </p>
                  </div>
                </div>
              ) : correctionDetails.status === 'rejected' ? (
                <div className="mb-6">
                  <div className="glass-card p-4 rounded-xl border-2 border-yellow-500/50 bg-yellow-500/5">
                    <p className="text-yellow-300">
                      The professor reviewed your flag and determined the original response was correct.
                    </p>
                  </div>
                </div>
              ) : null}

              {/* Reviewed Info */}
              {correctionDetails.reviewed_at && (
                <div className="mb-6 text-xs text-gray-500">
                  Reviewed {correctionDetails.reviewed_by ? `by ${correctionDetails.reviewed_by}` : ''} on {new Date(correctionDetails.reviewed_at).toLocaleString()}
                </div>
              )}

              <motion.button
                onClick={() => {
                  setViewingCorrection(null);
                  setCorrectionDetails(null);
                }}
                className="w-full px-6 py-3 glass rounded-xl text-white"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Close
              </motion.button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Flag Dialog with AnimatePresence */}
      <AnimatePresence>
        {showFlagDialog && (
          <motion.div
            className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={() => {
              setShowFlagDialog(false);
              setFlagReason('');
              setFlaggedMessage(null);
            }}
          >
            <motion.div
              className="glass-strong rounded-2xl p-8 max-w-md w-full shadow-layers-purple"
              initial={{ scale: 0.8, y: 50, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.8, y: 50, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold mb-4 gradient-shine">Flag Incorrect Response</h3>
              <p className="text-sm text-gray-300 mb-6">
                Help us improve! Tell us why this response is incorrect:
              </p>
              <motion.textarea
                value={flagReason}
                onChange={(e) => setFlagReason(e.target.value)}
                className="w-full glass-card text-white placeholder-gray-400 rounded-xl p-4 h-32 focus:outline-none input-glow resize-none"
                placeholder="e.g., The course is only offered in Fall, not Spring"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
              />
              <div className="flex gap-3 mt-6">
                <motion.button
                  onClick={() => {
                    setShowFlagDialog(false);
                    setFlagReason('');
                    setFlaggedMessage(null);
                  }}
                  className="flex-1 px-6 py-3 glass rounded-xl text-white transition-all duration-300"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
                <motion.button
                  onClick={submitFlag}
                  disabled={!flagReason.trim()}
                  className="flex-1 px-6 py-3 text-white rounded-xl liquid-btn transition-all duration-300 disabled:opacity-50 font-medium shadow-layers-purple"
                  style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Submit
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
