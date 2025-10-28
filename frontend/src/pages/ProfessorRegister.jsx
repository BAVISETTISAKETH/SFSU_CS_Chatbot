import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Sparkles, ArrowLeft, User, Building2, Key, CheckCircle, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { sendOTP, verifyOTP, professorRegister } from '../services/api';

export default function ProfessorRegister() {
  const [step, setStep] = useState(1); // 1: Email/Name, 2: OTP, 3: Password
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    otp: '',
    password: '',
    confirmPassword: '',
    department: 'Computer Science'
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Step 1: Send OTP
  const handleSendOTP = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.name.trim()) {
      setError('Please enter your name');
      return;
    }

    if (!formData.username.trim()) {
      setError('Please enter a username');
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters long');
      return;
    }

    if (!formData.email.endsWith('@sfsu.edu')) {
      setError('Please use your SFSU email (@sfsu.edu)');
      return;
    }

    setLoading(true);

    try {
      const response = await sendOTP(formData.email, formData.name);
      setSuccess('OTP sent to your email! Please check your inbox.');
      setStep(2);

      // Show dev OTP if available (for testing)
      if (response.dev_otp) {
        setSuccess(`OTP sent! (Dev mode: ${response.dev_otp})`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Verify OTP
  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.otp.trim() || formData.otp.length !== 6) {
      setError('Please enter a valid 6-digit OTP');
      return;
    }

    setLoading(true);

    try {
      await verifyOTP(formData.email, formData.otp);
      setSuccess('Email verified! Now set your password.');
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid or expired OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Create Account
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }

    setLoading(true);

    try {
      await professorRegister({
        name: formData.name,
        username: formData.username,
        email: formData.email,
        password: formData.password,
        department: formData.department,
        otp: formData.otp
      });

      alert('Account created successfully! Please login.');
      navigate('/professor');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
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
        onClick={() => navigate('/professor')}
        className="absolute top-6 left-6 glass px-4 py-2 rounded-xl text-white flex items-center gap-2 transition-all duration-300 z-50"
        initial={{ x: -100, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        whileHover={{ scale: 1.05, x: -5 }}
        whileTap={{ scale: 0.95 }}
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Login
      </motion.button>

      {/* Registration Card */}
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
          <h1 className="text-4xl font-bold gradient-shine mb-2">Create Account</h1>
          <p className="text-gray-300">
            {step === 1 && 'Step 1: Enter your details'}
            {step === 2 && 'Step 2: Verify your email'}
            {step === 3 && 'Step 3: Set your password'}
          </p>
        </motion.div>

        {/* Progress Indicators */}
        <motion.div
          className="flex items-center justify-center gap-3 mb-8"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          {[1, 2, 3].map((i) => (
            <motion.div
              key={i}
              className={`h-2 rounded-full transition-all duration-500 ${
                step >= i ? 'w-12 bg-gradient-to-r from-purple-500 to-gold-500' : 'w-2 bg-gray-600'
              }`}
              animate={step >= i ? {
                boxShadow: [
                  "0 0 5px rgba(168, 85, 247, 0.5)",
                  "0 0 15px rgba(180, 151, 90, 0.6)",
                  "0 0 5px rgba(168, 85, 247, 0.5)"
                ]
              } : {}}
              transition={{ duration: 1.5, repeat: Infinity }}
            ></motion.div>
          ))}
        </motion.div>

        {/* Step 1: Email & Name */}
        <AnimatePresence mode="wait">
        {step === 1 && (
          <motion.form
            key="step1"
            onSubmit={handleSendOTP}
            className="space-y-5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="space-y-2">
              <label htmlFor="name" className="block text-sm font-medium text-gray-200">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                  placeholder="John Doe"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="username" className="block text-sm font-medium text-gray-200">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  minLength="3"
                  maxLength="50"
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                  placeholder="johndoe"
                />
              </div>
              <p className="text-xs text-gray-400 mt-1">Used for login (3-50 characters, no spaces)</p>
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-gray-200">
                SFSU Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                  placeholder="professor@sfsu.edu"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="department" className="block text-sm font-medium text-gray-200">
                Department
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Building2 className="w-5 h-5 text-gray-400" />
                </div>
                <select
                  id="department"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  required
                  className="w-full pl-12 pr-4 py-3 glass-card text-white rounded-xl focus:outline-none input-glow transition-all duration-300"
                  style={{
                    colorScheme: 'dark'
                  }}
                >
                  <option value="Computer Science" className="bg-slate-800 text-white">Computer Science</option>
                  <option value="Mathematics" className="bg-slate-800 text-white">Mathematics</option>
                  <option value="Engineering" className="bg-slate-800 text-white">Engineering</option>
                  <option value="Other" className="bg-slate-800 text-white">Other</option>
                </select>
              </div>
            </div>

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

            <motion.button
              type="submit"
              disabled={loading}
              className="w-full text-white font-medium py-4 px-6 rounded-xl liquid-btn transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-layers-purple"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
              whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
              whileTap={{ scale: 0.98 }}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <motion.div
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  ></motion.div>
                  Sending OTP...
                </div>
              ) : (
                'Send OTP'
              )}
            </motion.button>
          </motion.form>
        )}

        {/* Step 2: OTP Verification */}
        {step === 2 && (
          <motion.form
            key="step2"
            onSubmit={handleVerifyOTP}
            className="space-y-5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <div className="text-center mb-4">
              <p className="text-sm text-gray-300">
                We've sent a 6-digit OTP to <span className="font-semibold gradient-shine">{formData.email}</span>
              </p>
            </div>

            <AnimatePresence>
              {success && (
                <motion.div
                  className="glass-card border-green-500/30 text-green-200 px-4 py-3 rounded-xl text-sm flex items-center gap-2"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
                >
                  <CheckCircle className="w-4 h-4" />
                  {success}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="space-y-2">
              <label htmlFor="otp" className="block text-sm font-medium text-gray-200">
                Enter OTP
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Key className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="otp"
                  name="otp"
                  type="text"
                  value={formData.otp}
                  onChange={handleChange}
                  required
                  maxLength="6"
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300 text-center text-2xl tracking-widest"
                  placeholder="000000"
                />
              </div>
            </div>

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

            <div className="flex gap-3">
              <motion.button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 glass px-6 py-3 rounded-xl text-white transition-all duration-300"
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                Back
              </motion.button>
              <motion.button
                type="submit"
                disabled={loading}
                className="flex-1 text-white font-medium py-3 px-6 rounded-xl liquid-btn transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-layers-purple"
                style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
                whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <div className="flex items-center justify-center gap-2">
                    <motion.div
                      className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    ></motion.div>
                  </div>
                ) : (
                  'Verify'
                )}
              </motion.button>
            </div>

            <motion.button
              type="button"
              onClick={handleSendOTP}
              className="w-full text-sm text-gray-400 hover:text-purple-400 transition-all duration-300"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Didn't receive OTP? Resend
            </motion.button>
          </motion.form>
        )}

        {/* Step 3: Password */}
        {step === 3 && (
          <motion.form
            key="step3"
            onSubmit={handleSubmit}
            className="space-y-5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            <AnimatePresence>
              {success && (
                <motion.div
                  className="glass-card border-green-500/30 text-green-200 px-4 py-3 rounded-xl text-sm flex items-center gap-2"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.3 }}
                >
                  <CheckCircle className="w-4 h-4" />
                  {success}
                </motion.div>
              )}
            </AnimatePresence>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-gray-200">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                  placeholder="At least 6 characters"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-200">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full pl-12 pr-4 py-3 glass-card text-white placeholder-gray-400 rounded-xl focus:outline-none input-glow transition-all duration-300"
                  placeholder="Confirm your password"
                />
              </div>
            </div>

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

            <motion.button
              type="submit"
              disabled={loading}
              className="w-full text-white font-medium py-4 px-6 rounded-xl liquid-btn transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-layers-purple"
              style={{background: 'linear-gradient(135deg, #4B2E83 0%, #B4975A 100%)'}}
              whileHover={{ scale: 1.02, boxShadow: "0 0 30px rgba(75, 46, 131, 0.6)" }}
              whileTap={{ scale: 0.98 }}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <motion.div
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  ></motion.div>
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </motion.button>
          </motion.form>
        )}
        </AnimatePresence>

        {/* Login Link */}
        <motion.div
          className="mt-6 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <p className="text-sm text-gray-300">
            Already have an account?{' '}
            <motion.button
              onClick={() => navigate('/professor')}
              className="font-medium transition-all duration-300 gradient-shine"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Login here
            </motion.button>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
