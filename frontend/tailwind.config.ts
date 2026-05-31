import type { Config } from "tailwindcss";
import typography from "@tailwindcss/typography";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: "#102126",
        mist: "#edf7f5",
        teal: "#0f766e",
        coral: "#f9735b"
      }
    }
  },
  plugins: [typography]
};

export default config;
