/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      boxShadow: {
        soft: '0 10px 30px rgba(15, 23, 42, 0.08)',
      },
      colors: {
        brand: {
          50: '#eef7ff',
          100: '#d9edff',
          200: '#b8ddff',
          300: '#84c8ff',
          400: '#4dabff',
          500: '#1f8fff',
          600: '#0b6fe0',
          700: '#0c59b3',
          800: '#114b90',
          900: '#143f75',
        },
      },
    },
  },
  plugins: [],
}
