import { motion } from 'framer-motion';

export default function AlliGatorIcon({ className = "w-8 h-8" }) {
  return (
    <svg
      className={className}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Outer Ring - Rotating Knowledge Circle */}
      <motion.circle
        cx="50"
        cy="50"
        r="45"
        stroke="url(#ringGradient)"
        strokeWidth="3"
        fill="none"
        opacity="0.95"
        strokeDasharray="8 4"
        animate={{
          rotate: 360,
          strokeDashoffset: [0, -50]
        }}
        transition={{
          rotate: { duration: 20, repeat: Infinity, ease: "linear" },
          strokeDashoffset: { duration: 3, repeat: Infinity, ease: "linear" }
        }}
        style={{ originX: "50%", originY: "50%" }}
      />

      {/* Inner Rotating Orbits - 3 Paths */}
      <motion.ellipse
        cx="50"
        cy="50"
        rx="35"
        ry="20"
        stroke="url(#orbitGradient1)"
        strokeWidth="2.5"
        fill="none"
        opacity="0.75"
        animate={{
          rotate: [0, 360]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{ originX: "50%", originY: "50%" }}
      />

      <motion.ellipse
        cx="50"
        cy="50"
        rx="35"
        ry="20"
        stroke="url(#orbitGradient2)"
        strokeWidth="2.5"
        fill="none"
        opacity="0.75"
        animate={{
          rotate: [60, 420]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{ originX: "50%", originY: "50%" }}
      />

      <motion.ellipse
        cx="50"
        cy="50"
        rx="35"
        ry="20"
        stroke="url(#orbitGradient3)"
        strokeWidth="2.5"
        fill="none"
        opacity="0.75"
        animate={{
          rotate: [120, 480]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{ originX: "50%", originY: "50%" }}
      />

      {/* Central Star Burst - Knowledge Core */}
      <motion.g>
        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => (
          <motion.line
            key={i}
            x1="50"
            y1="50"
            x2={50 + Math.cos((angle * Math.PI) / 180) * 12}
            y2={50 + Math.sin((angle * Math.PI) / 180) * 12}
            stroke="url(#coreGradient)"
            strokeWidth="3"
            strokeLinecap="round"
            animate={{
              x2: [
                50 + Math.cos((angle * Math.PI) / 180) * 12,
                50 + Math.cos((angle * Math.PI) / 180) * 16,
                50 + Math.cos((angle * Math.PI) / 180) * 12
              ],
              y2: [
                50 + Math.sin((angle * Math.PI) / 180) * 12,
                50 + Math.sin((angle * Math.PI) / 180) * 16,
                50 + Math.sin((angle * Math.PI) / 180) * 12
              ],
              opacity: [0.95, 1, 0.95]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.1,
              ease: "easeInOut"
            }}
          />
        ))}
      </motion.g>

      {/* Central Hexagon - AI Brain Core */}
      <motion.path
        d="M 50 35 L 63 42.5 L 63 57.5 L 50 65 L 37 57.5 L 37 42.5 Z"
        fill="url(#hexGradient)"
        stroke="url(#hexStroke)"
        strokeWidth="3"
        animate={{
          scale: [1, 1.08, 1],
          opacity: [1, 1, 1]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        style={{ originX: "50%", originY: "50%" }}
      />

      {/* Inner Hexagon Lines - Neural Network */}
      <motion.g>
        <motion.line
          x1="50" y1="35"
          x2="50" y2="50"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 0
          }}
        />
        <motion.line
          x1="50" y1="50"
          x2="63" y2="42.5"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 0.3
          }}
        />
        <motion.line
          x1="50" y1="50"
          x2="63" y2="57.5"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 0.6
          }}
        />
        <motion.line
          x1="50" y1="50"
          x2="50" y2="65"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 0.9
          }}
        />
        <motion.line
          x1="50" y1="50"
          x2="37" y2="57.5"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 1.2
          }}
        />
        <motion.line
          x1="50" y1="50"
          x2="37" y2="42.5"
          stroke="url(#neuralGradient)"
          strokeWidth="2.5"
          animate={{
            opacity: [0.6, 1, 0.6]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: 1.5
          }}
        />
      </motion.g>

      {/* Central Core Dot - Pulsing Intelligence */}
      <motion.circle
        cx="50"
        cy="50"
        r="5"
        fill="url(#coreGlow)"
        animate={{
          r: [5, 7, 5],
          opacity: [1, 1, 1]
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Floating Particles - Data Flow */}
      {[...Array(6)].map((_, i) => {
        const angle = (i * 60) * Math.PI / 180;
        const radius = 28;
        return (
          <motion.circle
            key={`particle-${i}`}
            cx={50 + Math.cos(angle) * radius}
            cy={50 + Math.sin(angle) * radius}
            r="3"
            fill="url(#particleGradient)"
            animate={{
              cx: [
                50 + Math.cos(angle) * radius,
                50 + Math.cos(angle + 0.5) * (radius + 5),
                50 + Math.cos(angle) * radius
              ],
              cy: [
                50 + Math.sin(angle) * radius,
                50 + Math.sin(angle + 0.5) * (radius + 5),
                50 + Math.sin(angle) * radius
              ],
              opacity: [0.7, 1, 0.7],
              scale: [1, 1.3, 1]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              delay: i * 0.5,
              ease: "easeInOut"
            }}
          />
        );
      })}

      {/* Corner Accent Symbols - Guide Markers */}
      {[0, 90, 180, 270].map((angle, i) => {
        const x = 50 + Math.cos((angle * Math.PI) / 180) * 42;
        const y = 50 + Math.sin((angle * Math.PI) / 180) * 42;
        return (
          <motion.g key={`accent-${i}`}>
            <motion.circle
              cx={x}
              cy={y}
              r="4"
              fill="url(#accentGradient)"
              animate={{
                scale: [1, 1.4, 1],
                opacity: [0.8, 1, 0.8]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "easeInOut"
              }}
              style={{ originX: `${x}px`, originY: `${y}px` }}
            />
          </motion.g>
        );
      })}

      {/* Gradients */}
      <defs>
        {/* Ring Gradient - SFSU Purple to Gold */}
        <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#4B2E83" />
          <stop offset="50%" stopColor="#6B4FA3" />
          <stop offset="100%" stopColor="#B4975A" />
        </linearGradient>

        {/* Orbit Gradients */}
        <linearGradient id="orbitGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#6B4FA3" stopOpacity="1" />
          <stop offset="100%" stopColor="#D4B76A" stopOpacity="1" />
        </linearGradient>

        <linearGradient id="orbitGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#8B6FC3" stopOpacity="1" />
          <stop offset="100%" stopColor="#F4D78A" stopOpacity="1" />
        </linearGradient>

        <linearGradient id="orbitGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#D4B76A" stopOpacity="1" />
          <stop offset="100%" stopColor="#6B4FA3" stopOpacity="1" />
        </linearGradient>

        {/* Core Gradient */}
        <linearGradient id="coreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F4D78A" />
          <stop offset="100%" stopColor="#D4B76A" />
        </linearGradient>

        {/* Hexagon Gradient */}
        <radialGradient id="hexGradient">
          <stop offset="0%" stopColor="#8B6FC3" stopOpacity="1" />
          <stop offset="100%" stopColor="#6B4FA3" stopOpacity="1" />
        </radialGradient>

        <linearGradient id="hexStroke" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D4B76A" />
          <stop offset="100%" stopColor="#F4D78A" />
        </linearGradient>

        {/* Neural Gradient */}
        <linearGradient id="neuralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F4D78A" />
          <stop offset="100%" stopColor="#FFFFFF" />
        </linearGradient>

        {/* Core Glow */}
        <radialGradient id="coreGlow">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="50%" stopColor="#F4D78A" />
          <stop offset="100%" stopColor="#D4B76A" />
        </radialGradient>

        {/* Particle Gradient */}
        <radialGradient id="particleGradient">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="1" />
          <stop offset="100%" stopColor="#D4B76A" stopOpacity="1" />
        </radialGradient>

        {/* Accent Gradient */}
        <radialGradient id="accentGradient">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="50%" stopColor="#D4B76A" />
          <stop offset="100%" stopColor="#6B4FA3" />
        </radialGradient>
      </defs>
    </svg>
  );
}
