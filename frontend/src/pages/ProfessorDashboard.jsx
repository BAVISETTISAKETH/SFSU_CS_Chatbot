import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPendingCorrections, reviewCorrection, getStats, getTrendingQuestions } from '../services/api';
import { CheckCircle, XCircle, Edit, LogOut, BarChart, MessageSquare, Sparkles, TrendingUp, Home, ThumbsUp, ThumbsDown, Zap, Flame, Calendar } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import LiquidGlassBackground from '../components/LiquidGlassBackground';
import AlliGatorIcon from '../components/AlliGatorIcon';

export default function ProfessorDashboard() {
  const [activeTab, setActiveTab] = useState('corrections');
  const [corrections, setCorrections] = useState([]);
  const [stats, setStats] = useState(null);
  const [trendingData, setTrendingData] = useState(null);
  const [trendingPeriod, setTrendingPeriod] = useState(7); // Default 7 days
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [correctedResponse, setCorrectedResponse] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadData();
  }, [activeTab, trendingPeriod]);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      if (activeTab === 'corrections') {
        const data = await getPendingCorrections();
        setCorrections(data);
      } else if (activeTab === 'stats') {
        const data = await getStats();
        setStats(data);
      } else if (activeTab === 'trending') {
        const data = await getTrendingQuestions(10, trendingPeriod);
        setTrendingData(data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load data');
      if (err.response?.status === 401) {
        localStorage.removeItem('professorToken');
        navigate('/professor');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('professorToken');
    navigate('/professor');
  };

  const handleReview = async (correctionId, action, correctedText = '') => {
    try {
      await reviewCorrection(correctionId, action, correctedText);
      await loadData();
      setEditingId(null);
      setCorrectedResponse('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to review correction');
    }
  };

  const startCorrection = (correction) => {
    setEditingId(correction._id);
    setCorrectedResponse(correction.botResponse);
  };

  const submitCorrection = (correctionId) => {
    handleReview(correctionId, 'approve', correctedResponse);
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-950">
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
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-3 md:py-4 flex items-center justify-between">
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
                  Professor Dashboard
                </h1>
                <p className="text-xs md:text-sm hidden md:block" style={{color: '#DCC890'}}>
                  Manage chatbot corrections & insights
                </p>
              </div>
            </div>
          </div>
          <motion.button
            onClick={handleLogout}
            className="glass px-3 md:px-6 py-2 md:py-2.5 rounded-xl text-white flex items-center gap-2 transition-all duration-300 shadow-layers"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </motion.button>
        </div>
      </motion.header>

      {/* Main Content */}
      <motion.div
        className="relative z-10 max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        {/* Tab Navigation - Enhanced */}
        <motion.div
          className="liquid-panel rounded-2xl mb-6 p-2 flex gap-2 shadow-layers-purple"
          initial={{ scale: 0.95 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200 }}
        >
          <motion.button
            onClick={() => setActiveTab('corrections')}
            className={`flex-1 px-4 md:px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
              activeTab === 'corrections'
                ? 'text-white shadow-layers-purple'
                : 'text-gray-300'
            }`}
            style={activeTab === 'corrections' ? {background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'} : {}}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <MessageSquare className="w-4 h-4 md:w-5 md:h-5" />
            <span className="hidden sm:inline">Pending Corrections</span>
            <span className="sm:hidden">Corrections</span>
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('stats')}
            className={`flex-1 px-4 md:px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
              activeTab === 'stats'
                ? 'text-white shadow-layers-purple'
                : 'text-gray-300'
            }`}
            style={activeTab === 'stats' ? {background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'} : {}}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <BarChart className="w-4 h-4 md:w-5 md:h-5" />
            Stats
          </motion.button>
          <motion.button
            onClick={() => setActiveTab('trending')}
            className={`flex-1 px-4 md:px-6 py-3 rounded-xl font-medium transition-all duration-300 flex items-center justify-center gap-2 ${
              activeTab === 'trending'
                ? 'text-white shadow-layers-purple'
                : 'text-gray-300'
            }`}
            style={activeTab === 'trending' ? {background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'} : {}}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            <Flame className="w-4 h-4 md:w-5 md:h-5" />
            <span className="hidden sm:inline">Trending</span>
            <span className="sm:hidden">Hot</span>
          </motion.button>
        </motion.div>

        {/* Content Area */}
        <motion.div
          className="liquid-card rounded-2xl p-6 md:p-8 shadow-layers-purple"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <AnimatePresence>
            {error && (
              <motion.div
                className="liquid-card border-red-500/30 text-red-200 px-6 py-4 rounded-xl mb-6"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {loading ? (
            <div className="text-center py-16">
              <motion.div
                className="w-16 h-16 border-4 rounded-full mx-auto"
                style={{borderColor: '#6B4FA3', borderTopColor: 'transparent'}}
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              <p className="text-gray-300 mt-4">Loading...</p>
            </div>
          ) : activeTab === 'trending' ? (
            <div className="space-y-6">
              {/* Period Selector */}
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold gradient-shine flex items-center gap-2">
                    <Flame className="w-6 h-6" />
                    Trending Questions
                  </h2>
                  <p className="text-gray-400 text-sm mt-1">Most frequently asked questions</p>
                </div>
                <div className="flex gap-2">
                  {[7, 14, 30].map((days) => (
                    <motion.button
                      key={days}
                      onClick={() => setTrendingPeriod(days)}
                      className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                        trendingPeriod === days
                          ? 'text-white shadow-layers'
                          : 'glass text-gray-300'
                      }`}
                      style={trendingPeriod === days ? {background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'} : {}}
                      whileHover={{ scale: 1.05, y: -2 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {days}d
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Summary Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <motion.div
                  className="glass-card p-4 rounded-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <div className="text-sm text-gray-400 mb-1">Total Queries</div>
                  <div className="text-3xl font-bold gradient-shine">{trendingData?.total_queries || 0}</div>
                </motion.div>
                <motion.div
                  className="glass-card p-4 rounded-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <div className="text-sm text-gray-400 mb-1">Time Period</div>
                  <div className="text-3xl font-bold gradient-shine">{trendingData?.period_days || 0} days</div>
                </motion.div>
                <motion.div
                  className="glass-card p-4 rounded-xl"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="text-sm text-gray-400 mb-1">Unique Questions</div>
                  <div className="text-3xl font-bold gradient-shine">{trendingData?.trending_questions?.length || 0}</div>
                </motion.div>
              </div>

              {/* Trending Questions List */}
              {trendingData?.trending_questions && trendingData.trending_questions.length > 0 ? (
                <div className="space-y-4">
                  <AnimatePresence mode="popLayout">
                    {trendingData.trending_questions.map((item, index) => (
                      <motion.div
                        key={index}
                        className="liquid-card p-6 rounded-2xl tilt-card"
                        initial={{ opacity: 0, x: -20, scale: 0.95 }}
                        animate={{ opacity: 1, x: 0, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{
                          duration: 0.4,
                          delay: index * 0.05,
                          type: "spring",
                          stiffness: 300
                        }}
                        whileHover={{ y: -4, scale: 1.01 }}
                        layout
                      >
                        <div className="flex items-start gap-4">
                          {/* Rank Badge */}
                          <motion.div
                            className="flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl"
                            style={{
                              background: index < 3
                                ? 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'
                                : 'linear-gradient(135deg, rgba(75, 46, 131, 0.3) 0%, rgba(180, 151, 90, 0.3) 100%)'
                            }}
                            animate={index < 3 ? {
                              boxShadow: [
                                "0 0 20px rgba(75, 46, 131, 0.5)",
                                "0 0 40px rgba(180, 151, 90, 0.6)",
                                "0 0 20px rgba(75, 46, 131, 0.5)"
                              ]
                            } : {}}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            <span className="gradient-shine">#{index + 1}</span>
                          </motion.div>

                          {/* Question Content */}
                          <div className="flex-1">
                            <p className="text-white text-lg mb-3">{item.question}</p>
                            <div className="flex items-center gap-4 text-sm">
                              <div className="flex items-center gap-2 text-purple-300">
                                <MessageSquare className="w-4 h-4" />
                                <span className="font-medium">{item.count} times</span>
                              </div>
                              <div className="flex items-center gap-2 text-gold-300">
                                <TrendingUp className="w-4 h-4" />
                                <span className="font-medium">{item.percentage}% of total</span>
                              </div>
                            </div>
                          </div>

                          {/* Quick Action Button */}
                          <motion.button
                            className="flex-shrink-0 glass px-4 py-2 rounded-xl text-white text-sm font-medium"
                            whileHover={{ scale: 1.05, y: -2 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => {
                              // TODO: Add "Create Answer" functionality
                              alert('Create answer feature coming soon!');
                            }}
                          >
                            Create Answer
                          </motion.button>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              ) : (
                <motion.div
                  className="text-center py-16"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <motion.div
                    className="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4"
                    style={{background: 'linear-gradient(135deg, rgba(107, 79, 163, 0.3) 0%, rgba(212, 183, 106, 0.3) 100%)'}}
                    animate={{ scale: [1, 1.05, 1], rotate: [0, 5, -5, 0] }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <Flame className="w-12 h-12" style={{color: '#B4975A'}} />
                  </motion.div>
                  <p className="text-gray-200 text-lg font-medium">No trending questions yet</p>
                  <p className="text-gray-400 text-sm mt-2">Check back when more students start asking questions!</p>
                </motion.div>
              )}
            </div>
          ) : activeTab === 'corrections' ? (
            <div className="space-y-6">
              {corrections.length === 0 ? (
                <motion.div
                  className="text-center py-16"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: "spring", stiffness: 200 }}
                >
                  <motion.div
                    className="w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4"
                    style={{background: 'linear-gradient(135deg, rgba(107, 79, 163, 0.3) 0%, rgba(212, 183, 106, 0.3) 100%)'}}
                    animate={{
                      scale: [1, 1.05, 1],
                      rotate: [0, 5, -5, 0]
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  >
                    <CheckCircle className="w-12 h-12" style={{color: '#6B4FA3'}} />
                  </motion.div>
                  <p className="text-gray-200 text-lg font-medium">No pending corrections</p>
                  <p className="text-gray-400 text-sm mt-2">All caught up! Great work! 🎉</p>
                </motion.div>
              ) : (
                <AnimatePresence mode="popLayout">
                  {corrections.map((correction, index) => (
                    <motion.div
                      key={correction._id}
                      className="liquid-card rounded-2xl p-6 tilt-card shadow-layers"
                      initial={{ opacity: 0, y: 20, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{
                        duration: 0.4,
                        delay: index * 0.1,
                        type: "spring",
                        stiffness: 300,
                        damping: 30
                      }}
                      whileHover={{ y: -4, scale: 1.01 }}
                      layout
                    >
                    {/* Student Query */}
                    <div className="mb-4">
                      <div className="text-sm font-medium text-purple-300 mb-2 flex items-center gap-2">
                        <MessageSquare className="w-4 h-4" />
                        Student Query:
                      </div>
                      <div className="text-white bg-white/5 p-4 rounded-xl">{correction.query}</div>
                    </div>

                    {/* Bot Response */}
                    <div className="mb-4">
                      <div className="text-sm font-medium text-blue-300 mb-2 flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Bot Response:
                      </div>
                      {editingId === correction._id ? (
                        <textarea
                          value={correctedResponse}
                          onChange={(e) => setCorrectedResponse(e.target.value)}
                          className="w-full px-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow resize-none min-h-32"
                        />
                      ) : (
                        <div className="text-white bg-white/5 p-4 rounded-xl">
                          {correction.botResponse}
                        </div>
                      )}
                    </div>

                    {/* Student Reason */}
                    <div className="mb-6">
                      <div className="text-sm font-medium text-pink-300 mb-2 flex items-center gap-2">
                        <Edit className="w-4 h-4" />
                        Student Reason:
                      </div>
                      <div className="text-gray-300 italic bg-white/5 p-4 rounded-xl">
                        "{correction.reason}"
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      {editingId === correction._id ? (
                        <>
                          <motion.button
                            onClick={() => submitCorrection(correction._id)}
                            className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl liquid-btn transition-all duration-300 flex items-center justify-center gap-2 font-medium shadow-layers"
                            whileHover={{ scale: 1.02, y: -2, boxShadow: "0 0 30px rgba(16, 185, 129, 0.6)" }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <CheckCircle size={18} />
                            <span className="hidden sm:inline">Submit Correction</span>
                            <span className="sm:hidden">Submit</span>
                          </motion.button>
                          <motion.button
                            onClick={() => {
                              setEditingId(null);
                              setCorrectedResponse('');
                            }}
                            className="flex-1 glass text-white px-6 py-3 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 font-medium"
                            whileHover={{ scale: 1.02, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            Cancel
                          </motion.button>
                        </>
                      ) : (
                        <>
                          <motion.button
                            onClick={() => handleReview(correction._id, 'approve')}
                            className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-xl liquid-btn transition-all duration-300 flex items-center justify-center gap-2 font-medium shadow-layers"
                            whileHover={{ scale: 1.02, y: -2, boxShadow: "0 0 30px rgba(16, 185, 129, 0.6)" }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <CheckCircle size={18} />
                            <span className="hidden sm:inline">Approve</span>
                            <span className="sm:hidden">✓</span>
                          </motion.button>
                          <motion.button
                            onClick={() => startCorrection(correction)}
                            className="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-xl liquid-btn transition-all duration-300 flex items-center justify-center gap-2 font-medium shadow-layers"
                            whileHover={{ scale: 1.02, y: -2, boxShadow: "0 0 30px rgba(59, 130, 246, 0.6)" }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <Edit size={18} />
                            <span className="hidden sm:inline">Correct</span>
                            <span className="sm:hidden">✏</span>
                          </motion.button>
                          <motion.button
                            onClick={() => handleReview(correction._id, 'reject')}
                            className="flex-1 bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-3 rounded-xl liquid-btn transition-all duration-300 flex items-center justify-center gap-2 font-medium shadow-layers"
                            whileHover={{ scale: 1.02, y: -2, boxShadow: "0 0 30px rgba(239, 68, 68, 0.6)" }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <XCircle size={18} />
                            <span className="hidden sm:inline">Reject</span>
                            <span className="sm:hidden">✕</span>
                          </motion.button>
                        </>
                      )}
                    </div>
                  </motion.div>
                ))}
                </AnimatePresence>
              )}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Main Stats Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Total Chats Card with Motion */}
              <motion.div
                className="gradient-border transition-all duration-300 tilt-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="gradient-border-content">
                  <div className="flex items-center gap-3 mb-4">
                    <motion.div
                      className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-layers-purple"
                      whileHover={{ rotate: 360, scale: 1.1 }}
                      transition={{ duration: 0.5 }}
                    >
                      <MessageSquare className="w-6 h-6 text-white" />
                    </motion.div>
                    <div className="text-sm font-medium text-purple-300">Total Chats</div>
                  </div>
                  <motion.div
                    className="text-4xl font-bold gradient-text-purple"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: 0.3 }}
                  >
                    {stats?.totalChats || 0}
                  </motion.div>
                  <div className="mt-2 flex items-center gap-1 text-sm text-gray-400">
                    <TrendingUp className="w-4 h-4" />
                    All time
                  </div>
                </div>
              </motion.div>

              {/* Total Corrections Card with Motion */}
              <motion.div
                className="gradient-border transition-all duration-300 tilt-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="gradient-border-content">
                  <div className="flex items-center gap-3 mb-4">
                    <motion.div
                      className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-layers"
                      whileHover={{ rotate: 360, scale: 1.1 }}
                      transition={{ duration: 0.5 }}
                    >
                      <Edit className="w-6 h-6 text-white" />
                    </motion.div>
                    <div className="text-sm font-medium text-blue-300">Total Corrections</div>
                  </div>
                  <motion.div
                    className="text-4xl font-bold gradient-text-blue"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: 0.4 }}
                  >
                    {stats?.totalCorrections || 0}
                  </motion.div>
                  <div className="mt-2 flex items-center gap-1 text-sm text-gray-400">
                    <TrendingUp className="w-4 h-4" />
                    All time
                  </div>
                </div>
              </motion.div>

              {/* Verified Facts Card with Motion */}
              <motion.div
                className="gradient-border transition-all duration-300 tilt-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <div className="gradient-border-content">
                  <div className="flex items-center gap-3 mb-4">
                    <motion.div
                      className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-layers"
                      whileHover={{ rotate: 360, scale: 1.1 }}
                      transition={{ duration: 0.5 }}
                    >
                      <CheckCircle className="w-6 h-6 text-white" />
                    </motion.div>
                    <div className="text-sm font-medium text-green-300">Verified Facts</div>
                  </div>
                  <motion.div
                    className="text-4xl font-bold gradient-shine"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, delay: 0.5 }}
                  >
                    {stats?.verifiedFacts || 0}
                  </motion.div>
                  <div className="mt-2 flex items-center gap-1 text-sm text-gray-400">
                    <TrendingUp className="w-4 h-4" />
                    All time
                  </div>
                </div>
              </motion.div>
              </div>

              {/* Feedback & Satisfaction Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Satisfaction Rate Card */}
                <motion.div
                  className="gradient-border transition-all duration-300 tilt-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                >
                  <div className="gradient-border-content">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-sm font-medium text-yellow-300">Satisfaction Rate</div>
                      <motion.div
                        className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-amber-500 rounded-xl flex items-center justify-center shadow-layers"
                        whileHover={{ rotate: 360, scale: 1.1 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Zap className="w-6 h-6 text-white" />
                      </motion.div>
                    </div>
                    <motion.div
                      className="text-5xl font-bold gradient-shine mb-2"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 200, delay: 0.6 }}
                    >
                      {stats?.feedbackStats?.satisfaction_rate || 0}%
                    </motion.div>
                    <div className="flex items-center gap-4 mt-4">
                      <div className="flex items-center gap-2 text-green-400">
                        <ThumbsUp className="w-4 h-4" />
                        <span className="text-sm font-medium">{stats?.feedbackStats?.thumbs_up || 0}</span>
                      </div>
                      <div className="flex items-center gap-2 text-red-400">
                        <ThumbsDown className="w-4 h-4" />
                        <span className="text-sm font-medium">{stats?.feedbackStats?.thumbs_down || 0}</span>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-400">
                      Based on {stats?.feedbackStats?.total_feedback || 0} total feedback responses
                    </div>
                  </div>
                </motion.div>

                {/* Response Time Card */}
                <motion.div
                  className="gradient-border transition-all duration-300 tilt-card"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  whileHover={{ scale: 1.05, y: -5 }}
                >
                  <div className="gradient-border-content">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-sm font-medium text-pink-300">Avg Response Time</div>
                      <motion.div
                        className="w-12 h-12 bg-gradient-to-br from-pink-500 to-rose-500 rounded-xl flex items-center justify-center shadow-layers"
                        whileHover={{ rotate: 360, scale: 1.1 }}
                        transition={{ duration: 0.5 }}
                      >
                        <Sparkles className="w-6 h-6 text-white" />
                      </motion.div>
                    </div>
                    <motion.div
                      className="text-4xl font-bold gradient-shine mb-2"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 200, delay: 0.7 }}
                    >
                      {stats?.avgResponseTime || 0}ms
                    </motion.div>
                    <div className="mt-2 flex items-center gap-1 text-sm text-gray-400">
                      <TrendingUp className="w-4 h-4" />
                      Average across all queries
                    </div>
                  </div>
                </motion.div>
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
}
