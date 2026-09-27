import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Matte Cream Surface Tokens (from docs/design/design-tokens.md)
        surface: {
          canvas: "#FAF8F5",
          card: "#FFFFFF",
          subtle: "#F4F0E8",
          muted: "#ECE7DC",
        },
        // Borders & Dividers
        border: {
          subtle: "#E8E2D8",
          default: "#D8D1C4",
          strong: "#B8AE9D",
        },
        // High-contrast slate typography
        content: {
          primary: "#1C1917",
          secondary: "#44403C",
          muted: "#78716C",
          disabled: "#A8A29E",
        },
        // Meteorological Authority Accents (Navy)
        brand: {
          900: "#0F1D30",
          800: "#1E3A5F",
          700: "#2D5385",
          100: "#EBF1F8",
        },
        // Official IMD 4-Stage Warning Semantic Colors
        hazard: {
          green: {
            bg: "#EDF7ED",
            border: "#C8E6C9",
            text: "#1E4620",
            dot: "#2E7D32",
          },
          yellow: {
            bg: "#FFFBE6",
            border: "#FFE58F",
            text: "#724E00",
            dot: "#D48806",
          },
          orange: {
            bg: "#FFF2E8",
            border: "#FFBB96",
            text: "#872900",
            dot: "#D4380D",
          },
          red: {
            bg: "#FFF1F0",
            border: "#FFA39E",
            text: "#820014",
            dot: "#CF1322",
          },
        },
        // Radar Reflectivity (dBZ) Scale
        dbz: {
          15: "#A8DADC",
          25: "#457B9D",
          35: "#2A9D8F",
          42: "#E9C46A",
          47: "#F4A261",
          52: "#E76F51",
          57: "#D90429",
          62: "#9D0208",
          68: "#6A040F",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "SF Mono", "Roboto Mono", "monospace"],
      },
      boxShadow: {
        matte: "0 1px 3px 0 rgba(28, 25, 23, 0.06), 0 1px 2px -1px rgba(28, 25, 23, 0.04)",
        "matte-md": "0 4px 8px -2px rgba(28, 25, 23, 0.08), 0 2px 4px -2px rgba(28, 25, 23, 0.05)",
        "matte-lg": "0 8px 16px -4px rgba(28, 25, 23, 0.09), 0 4px 6px -3px rgba(28, 25, 23, 0.05)",
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
        lg: "8px",
      },
    },
  },
  plugins: [],
};

export default config;
