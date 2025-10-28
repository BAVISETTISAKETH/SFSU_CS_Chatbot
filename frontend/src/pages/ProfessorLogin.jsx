import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, ArrowLeft, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { professorLogin } from '../services/api';

export default function ProfessorLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await professorLogin(username, password);
      localStorage.setItem('professorToken', response.access_token);
      navigate('/professor/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex items-center justify-center p-6 bg-slate-950">
      {/* Animated Background with Aurora Effect - DARK MODE */}
      <motion.div
        className="absolute inset-0 animate-gradient aurora-bg z-0 pointer-events-none"
        style={{
          background: 'linear-gradient(135deg, #000000 0%, #0a0a0a 20%, #1a1a1a 40%, #0f0f0f 60%, #050505 80%, #000000 100%)',
          backgroundSize: '400% 400%'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      ></motion.div>

      {/* Back Button */}
      <motion.button
        onClick={() => navigate('/')}
        className="absolute top-6 left-6 glass px-4 py-2 rounded-xl text-white flex items-center gap-2 transition-all duration-300 z-50"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        whileHover={{ scale: 1.05, x: -5 }}
        whileTap={{ scale: 0.95 }}
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Home
      </motion.button>

      {/* Login Card */}
      <motion.div
        className="glass-strong rounded-3xl p-10 w-full max-w-md relative z-40 shadow-layers-purple"
        style={{ pointerEvents: 'auto' }}
        initial={{ opacity: 0, y: 50, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{
          type: "spring",
          stiffness: 200,
          damping: 20,
          duration: 0.8
        }}
      >
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
        >
          <motion.div
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 shadow-layers-purple"
            style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
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
            <Shield className="w-10 h-10 text-white" />
          </motion.div>
          <h1 className="text-4xl font-bold gradient-shine mb-2">Professor Portal</h1>
          <p className="text-gray-300">Login to manage chatbot responses</p>
        </motion.div>

        {/* Form */}
        <motion.form
          onSubmit={handleSubmit}
          className="space-y-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          {/* Username Input */}
          <motion.div
            className="space-y-2"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            <label htmlFor="username" className="block text-sm font-medium text-gray-200">
              Username or Email
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <User className="w-5 h-5 text-gray-400" />
              </div>
              <motion.input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                placeholder="your_username or professor@sfsu.edu"
                whileFocus={{ scale: 1.01 }}
              />
            </div>
          </motion.div>

          {/* Password Input */}
          <motion.div
            className="space-y-2"
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.5 }}
          >
            <label htmlFor="password" className="block text-sm font-medium text-gray-200">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock className="w-5 h-5 text-gray-400" />
              </div>
              <motion.input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                placeholder="Enter your password"
                whileFocus={{ scale: 1.01 }}
              />
            </div>
          </motion.div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                className="glass-card border-red-500/30 text-red-200 px-4 py-3 rounded-xl text-sm"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={loading}
            className="w-full text-white font-medium py-4 px-6 rounded-xl liquid-btn transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-layers-purple"
            style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
            whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
            whileTap={{ scale: 0.98 }}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.5 }}
          >
            {loading ? (
              <div className="flex items-center justify-center gap-2">
                <motion.div
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                ></motion.div>
                Logging in...
              </div>
            ) : (
              'Login to Dashboard'
            )}
          </motion.button>
        </motion.form>

        {/* Create Account Link */}
        <motion.div
          className="mt-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.5 }}
        >
          <p className="text-sm text-gray-300">
            Don't have an account?{' '}
            <motion.button
              onClick={() => navigate('/professor/register')}
              className="font-medium transition-all duration-300 gradient-shine"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Create an account
            </motion.button>
          </p>
        </motion.div>

        {/* Demo Credentials */}
        <motion.div
          className="mt-6 pt-6 border-t border-white/10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9, duration: 0.5 }}
        >
          <p className="text-xs text-gray-400 text-center mb-2">Demo Credentials:</p>
          <div className="glass rounded-lg p-3 text-xs text-gray-300 space-y-1">
            <p><span style={{color: '#B4975A'}}>Username:</span> admin</p>
            <p><span style={{color: '#B4975A'}}>Password:</span> admin123</p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
