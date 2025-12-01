/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                display: ['Outfit', 'sans-serif'],
            },
            colors: {
                'cyber-black': '#050505',
                'cyber-gray': '#0a0a0a',
                'neon-blue': '#00f3ff',
                'neon-purple': '#bc13fe',
                'neon-pink': '#ff00ff',
                'danger-red': '#ff003c',
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(0, 243, 255, 0.2)' },
                    '100%': { boxShadow: '0 0 20px rgba(0, 243, 255, 0.6), 0 0 10px rgba(0, 243, 255, 0.4)' },
                },
            },
        },
    },
    plugins: [],
}
