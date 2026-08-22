import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0a0e27",
          card: "#111827",
          border: "#1e293b",
          surface: "#151c36",
        },
        cyber: {
          blue: "#3b82f6",
          cyan: "#00d4ff",
          green: "#10b981",
          red: "#ef4444",
          orange: "#f59e0b",
          purple: "#8b5cf6",
        },
      },
      keyframes: {
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 5px rgba(0, 212, 255, 0.2)" },
          "50%": { boxShadow: "0 0 20px rgba(0, 212, 255, 0.4)" },
        },
        "slide-in": {
          "0%": { transform: "translateX(-10px)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
      },
      animation: {
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "slide-in": "slide-in 0.3s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
