const { fontFamily } = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans]
      },
      colors: {
        brand: {
          DEFAULT: "#1D8F6E",
          foreground: "#F4FBF8",
          muted: "#0F4234"
        }
      }
    }
  },
  plugins: []
};
