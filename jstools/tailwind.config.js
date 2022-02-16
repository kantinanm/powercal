module.exports = {
  mode: "jit",
  content: ["../**/templates/*.html", "../**/templates/**/*.html"],
  theme: {
    extend: {
      screens: {
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
      },
      fontFamily: {
        sans: ["Kanit", "sans-serif"],
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      }
    },
  },
  variants: {},
  plugins: [require("tailwindcss"), require("autoprefixer")],
};
