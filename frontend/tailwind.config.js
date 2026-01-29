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
                // Legacy aliases - mapped to standard Tailwind colors for consistency
                // These can be removed once all legacy code is migrated
                'cyber-black': '#050505',
                'cyber-gray': '#0a0a0a',
                // Map legacy neon colors to Tailwind equivalents
                'neon-blue': '#22d3ee',    // cyan-400
                'neon-purple': '#a855f7',  // violet-500
                'neon-pink': '#ec4899',    // pink-500
                'danger-red': '#f43f5e',   // rose-500
                'neon-green': '#34d399',   // emerald-400
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}
