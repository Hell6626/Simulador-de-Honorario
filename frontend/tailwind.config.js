/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'custom-blue': '#2E3746',
        'custom-blue-light': '#3A4758',
        'custom-blue-dark': '#1E2532',
      },
    },
  },
  plugins: [],
};
