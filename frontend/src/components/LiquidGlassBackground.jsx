import { motion } from 'framer-motion';

export default function LiquidGlassBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Liquid Blob 1 - Purple */}
      <motion.div
        className="liquid-blob liquid-blob-purple liquid-flow"
        style={{
          width: '500px',
          height: '500px',
          top: '10%',
          left: '5%',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.6, scale: 1 }}
        transition={{ duration: 2 }}
      />

      {/* Liquid Blob 2 - Gold */}
      <motion.div
        className="liquid-blob liquid-blob-gold liquid-flow-slow"
        style={{
          width: '600px',
          height: '600px',
          top: '40%',
          right: '0%',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.5, scale: 1 }}
        transition={{ duration: 2.5, delay: 0.5 }}
      />

      {/* Liquid Blob 3 - Blue */}
      <motion.div
        className="liquid-blob liquid-blob-blue liquid-flow-fast"
        style={{
          width: '450px',
          height: '450px',
          bottom: '10%',
          left: '30%',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.4, scale: 1 }}
        transition={{ duration: 2, delay: 1 }}
      />

      {/* Liquid Blob 4 - Purple (smaller) */}
      <motion.div
        className="liquid-blob liquid-blob-purple liquid-flow"
        style={{
          width: '350px',
          height: '350px',
          top: '60%',
          left: '10%',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.5, scale: 1 }}
        transition={{ duration: 2.2, delay: 0.8 }}
      />

      {/* Liquid Blob 5 - Gold (smaller) */}
      <motion.div
        className="liquid-blob liquid-blob-gold liquid-flow-slow"
        style={{
          width: '400px',
          height: '400px',
          top: '20%',
          right: '20%',
        }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 0.45, scale: 1 }}
        transition={{ duration: 2.3, delay: 1.2 }}
      />
    </div>
  );
}
