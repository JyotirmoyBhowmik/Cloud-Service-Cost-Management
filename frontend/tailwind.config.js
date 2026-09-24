/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ceramic: {
          50: "#fafafc",
          100: "#f4f4f7",
          200: "#e9eaee",
          300: "#d3d5de",
          400: "#a0a4b5",
          500: "#6e7287",
          600: "#4f5263",
          700: "#363844",
          800: "#22232a",
          900: "#131418",
        },
        cloud: {
          azure: "#0078d4",
          aws: "#ff9900",
          gcp: "#4285f4",
          oci: "#f80000",
        },
        status: {
          green: "#10b981",
          amber: "#f59e0b",
          orange: "#f97316",
          red: "#ef4444",
          grey: "#94a3b8",
          blue: "#3b82f6",
        }
      },
      boxShadow: {
        'ceramic': '0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'ceramic-hover': '0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04)',
        'modal': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
      }
    },
  },
  plugins: [],
};
