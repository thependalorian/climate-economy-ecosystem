/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ACT brand colors
        "spring-green": "#B2DE26",
        "moss-green": "#394816",
        "midnight-forest": "#001818",
        "seafoam-blue": "#E0FFFF",
        "sand-gray": "#EBE9E1",
        // Keep existing colors for compatibility
        primary: "#B2DE26", // Map to spring-green
        secondary: "#394816", // Map to moss-green
        accent: "#E0FFFF", // Map to seafoam-blue
      },
      fontFamily: {
        'helvetica': ['Helvetica', 'Arial', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#B2DE26", // spring-green
          "primary-content": "#001818", // midnight-forest
          "secondary": "#394816", // moss-green
          "secondary-content": "#ffffff",
          "accent": "#E0FFFF", // seafoam-blue
          "neutral": "#001818", // midnight-forest
          "base-100": "#ffffff",
          "base-200": "#f9fafb",
          "base-300": "#EBE9E1", // sand-gray
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
      },
    ],
  },
};
