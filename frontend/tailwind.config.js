/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sfsu: {
          // Official SFSU Colors
          purple: '#4B2E83',      // Primary Purple
          gold: '#B4975A',        // Primary Gold

          // Supporting Purple Shades
          'purple-light': '#6B4FA3',
          'purple-lighter': '#8B70B8',
          'purple-dark': '#3A2366',
          'purple-darker': '#2A1A4D',

          // Supporting Gold Shades
          'gold-light': '#C9AD74',
          'gold-lighter': '#DCC890',
          'gold-dark': '#9B7F47',
          'gold-darker': '#826935',

          // Complementary Colors - DARK MODE (pure black/grey)
          cream: '#F5F3ED',       // Soft cream background
          charcoal: '#0a0a0a',    // Pure black with hint of grey
          slate: '#000000',       // Pure black for backgrounds
          white: '#FFFFFF',       // Pure white for highlights
        },
      },
    },
  },
  plugins: [],
}
