import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GraduationCap, BookOpen, Users, Sparkles, ArrowRight, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LandingPage() {
  const [hoveredSide, setHoveredSide] = useState(null);
  const navigate = useNavigate();

  return (
    <div className="h-screen relative overflow-hidden bg-slate-950">
      {/* Animated Background with Aurora Effect - DARK MODE */}
      <motion.div
        className="absolute inset-0 animate-gradient aurora-bg"
        style={{
          background: 'linear-gradient(135deg, #000000 0%, #0a0a0a 20%, #1a1a1a 40%, #0f0f0f 60%, #050505 80%, #000000 100%)',
          backgroundSize: '400% 400%'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1 }}
      ></motion.div>

      {/* Floating Particles with Enhanced Motion - DARKER */}
      <div className="absolute inset-0 opacity-15">
        <motion.div
          className="absolute top-10 left-10 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl morph-blob"
          style={{ background: '#4B2E83' }}
          animate={{
            y: [0, -30, 0],
            x: [0, 20, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        ></motion.div>
        <motion.div
          className="absolute top-10 right-10 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl morph-blob"
          style={{ background: '#1e40af' }}
          animate={{
            y: [0, 30, 0],
            x: [0, -20, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 1
          }}
        ></motion.div>
        <motion.div
          className="absolute bottom-10 left-1/2 w-72 h-72 rounded-full mix-blend-screen filter blur-3xl morph-blob"
          style={{ background: '#7e22ce' }}
          animate={{
            y: [0, -20, 0],
            x: [0, 15, -15, 0],
            scale: [1, 1.15, 1],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
        ></motion.div>
      </div>

      {/* Header with Enhanced Motion */}
      <motion.header
        className="relative z-10 glass-dark border-b border-white/10"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            className="flex items-center gap-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <motion.div
              className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-layers-purple neon-pulse"
              whileHover={{ scale: 1.1, rotate: 360 }}
              transition={{ duration: 0.6 }}
            >
              <Sparkles className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold gradient-shine">Gator Guide</h1>
              <p className="text-sm text-gray-300">Your AI-Powered SFSU Assistant</p>
            </div>
          </motion.div>

          {/* Navigation Links with Stagger Animation */}
          <motion.nav
            className="flex items-center gap-4"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <motion.button
              onClick={() => navigate('/about')}
              className="text-gray-300 hover:text-white transition-all duration-300"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              About
            </motion.button>
            <motion.button
              onClick={() => navigate('/faq')}
              className="text-gray-300 hover:text-white transition-all duration-300"
              whileHover={{ scale: 1.1, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              FAQ
            </motion.button>
            <motion.button
              onClick={() => navigate('/chat')}
              className="glass px-6 py-2 rounded-xl text-white font-medium hover-lift transition-all duration-300 liquid-btn"
              whileHover={{ scale: 1.05, boxShadow: "0 0 25px rgba(139, 92, 246, 0.5)" }}
              whileTap={{ scale: 0.98 }}
            >
              Start Chat
            </motion.button>
          </motion.nav>
        </div>
      </motion.header>

      {/* Split Screen Content */}
      <div className="relative z-10 h-[calc(100vh-80px)] flex flex-col md:flex-row">
        {/* Student Side with Enhanced Motion */}
        <motion.div
          className={`flex-1 relative cursor-pointer transition-all duration-700 ${
            hoveredSide === 'student' ? 'flex-[1.5]' : hoveredSide === 'professor' ? 'flex-[0.5]' : 'flex-1'
          }`}
          onMouseEnter={() => setHoveredSide('student')}
          onMouseLeave={() => setHoveredSide(null)}
          onClick={() => navigate('/chat')}
          initial={{ opacity: 0, x: -100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          whileHover={{ scale: 1.02 }}
        >
          {/* Gradient Overlay with Animation - DARK */}
          <motion.div
            className="absolute inset-0 backdrop-blur-sm"
            style={{
              background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(6, 95, 70, 0.4) 100%)'
            }}
            animate={{
              opacity: hoveredSide === 'student' ? 0.9 : 0.5
            }}
            transition={{ duration: 0.5 }}
          ></motion.div>

          {/* Animated Border Line */}
          <motion.div
            className="absolute right-0 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-white/50 to-transparent"
            animate={{
              opacity: [0.3, 1, 0.3]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          ></motion.div>

          {/* Content with 3D Transform */}
          <motion.div
            className="relative h-full flex flex-col items-center justify-center p-12"
            animate={{
              scale: hoveredSide === 'student' ? 1.05 : 1
            }}
            transition={{ duration: 0.5 }}
          >
            <motion.div
              className="w-32 h-32 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-3xl flex items-center justify-center mb-8 shadow-layers tilt-card"
              whileHover={{
                rotateY: 15,
                rotateX: 15,
                scale: 1.1
              }}
              animate={hoveredSide === 'student' ? {
                boxShadow: [
                  "0 0 20px rgba(59, 130, 246, 0.5)",
                  "0 0 40px rgba(59, 130, 246, 0.8)",
                  "0 0 20px rgba(59, 130, 246, 0.5)"
                ]
              } : {}}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <GraduationCap className="w-16 h-16 text-white" />
            </motion.div>

            <motion.h2
              className="text-5xl font-bold text-white mb-4 text-center gradient-shine"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              Student
            </motion.h2>
            <motion.p
              className="text-xl text-gray-200 text-center mb-8 max-w-md"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              Get instant answers about courses, faculty, and requirements
            </motion.p>

            <motion.div
              className="flex items-center gap-2 text-cyan-300 font-medium"
              whileHover={{ x: 10 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <BookOpen className="w-5 h-5" />
              <span>Continue as Student</span>
              <motion.div
                animate={{
                  x: hoveredSide === 'student' ? [0, 5, 0] : 0
                }}
                transition={{
                  duration: 1,
                  repeat: hoveredSide === 'student' ? Infinity : 0
                }}
              >
                <ArrowRight className="w-5 h-5" />
              </motion.div>
            </motion.div>

            {/* Feature Pills with Stagger Animation */}
            <motion.div
              className="mt-12 flex flex-wrap gap-3 justify-center max-w-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, staggerChildren: 0.1 }}
            >
              <motion.div
                className="glass px-4 py-2 rounded-full text-sm text-gray-200 interactive-glow"
                whileHover={{ scale: 1.1, y: -3 }}
                whileTap={{ scale: 0.95 }}
              >
                <Users className="w-4 h-4 inline mr-2" />
                Guest Access
              </motion.div>
              <motion.div
                className="glass px-4 py-2 rounded-full text-sm text-gray-200 interactive-glow"
                whileHover={{ scale: 1.1, y: -3 }}
                whileTap={{ scale: 0.95 }}
              >
                <Shield className="w-4 h-4 inline mr-2" />
                Registered Student
              </motion.div>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Professor Side with Enhanced Motion */}
        <motion.div
          className={`flex-1 relative cursor-pointer transition-all duration-700 ${
            hoveredSide === 'professor' ? 'flex-[1.5]' : hoveredSide === 'student' ? 'flex-[0.5]' : 'flex-1'
          }`}
          onMouseEnter={() => setHoveredSide('professor')}
          onMouseLeave={() => setHoveredSide(null)}
          onClick={() => navigate('/professor')}
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          whileHover={{ scale: 1.02 }}
        >
          {/* Gradient Overlay with Animation - DARK */}
          <motion.div
            className="absolute inset-0 backdrop-blur-sm"
            style={{
              background: 'linear-gradient(135deg, rgba(75, 46, 131, 0.4) 0%, rgba(126, 34, 206, 0.4) 100%)'
            }}
            animate={{
              opacity: hoveredSide === 'professor' ? 0.9 : 0.5
            }}
            transition={{ duration: 0.5 }}
          ></motion.div>

          {/* Content with 3D Transform */}
          <motion.div
            className="relative h-full flex flex-col items-center justify-center p-12"
            animate={{
              scale: hoveredSide === 'professor' ? 1.05 : 1
            }}
            transition={{ duration: 0.5 }}
          >
            <motion.div
              className="w-32 h-32 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center mb-8 shadow-layers-purple tilt-card"
              whileHover={{
                rotateY: -15,
                rotateX: 15,
                scale: 1.1
              }}
              animate={hoveredSide === 'professor' ? {
                boxShadow: [
                  "0 0 20px rgba(168, 85, 247, 0.5)",
                  "0 0 40px rgba(168, 85, 247, 0.8)",
                  "0 0 20px rgba(168, 85, 247, 0.5)"
                ]
              } : {}}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Shield className="w-16 h-16 text-white" />
            </motion.div>

            <motion.h2
              className="text-5xl font-bold text-white mb-4 text-center gradient-shine"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              Professor
            </motion.h2>
            <motion.p
              className="text-xl text-gray-200 text-center mb-8 max-w-md"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              Manage chatbot responses and review student feedback
            </motion.p>

            <motion.div
              className="flex items-center gap-2 text-pink-300 font-medium"
              whileHover={{ x: 10 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Shield className="w-5 h-5" />
              <span>Professor Portal</span>
              <motion.div
                animate={{
                  x: hoveredSide === 'professor' ? [0, 5, 0] : 0
                }}
                transition={{
                  duration: 1,
                  repeat: hoveredSide === 'professor' ? Infinity : 0
                }}
              >
                <ArrowRight className="w-5 h-5" />
              </motion.div>
            </motion.div>

            {/* Feature Pills with Stagger Animation */}
            <motion.div
              className="mt-12 flex flex-wrap gap-3 justify-center max-w-md"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.2, staggerChildren: 0.1 }}
            >
              {['Review Corrections', 'Verify Facts', 'View Analytics'].map((feature, idx) => (
                <motion.div
                  key={idx}
                  className="glass px-4 py-2 rounded-full text-sm text-gray-200 interactive-glow"
                  whileHover={{ scale: 1.1, y: -3 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.3 + idx * 0.1 }}
                >
                  {feature}
                </motion.div>
              ))}
            </motion.div>
          </motion.div>
        </motion.div>
      </div>

      {/* Bottom Hint with Enhanced Animation */}
      <motion.div
        className="absolute bottom-8 z-20 w-full flex justify-center items-center"
        initial={{ opacity: 0, y: 50 }}
        animate={{
          opacity: 1,
          y: [0, -10, 0]
        }}
        transition={{
          opacity: { delay: 1.5, duration: 0.5 },
          y: { delay: 2, duration: 2, repeat: Infinity, ease: "easeInOut" }
        }}
      >
        <motion.div
          className="glass-strong px-6 py-3 rounded-full"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <p className="text-gray-200 text-sm text-center whitespace-nowrap">
            Click on either side to continue
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
