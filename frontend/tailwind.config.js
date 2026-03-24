/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
            colors: {
                brand: {
                    50: '#FFF7F0',
                    100: '#FFE8D6',
                    200: '#FFC9A0',
                    300: '#FFA06B',
                    400: '#FF7A42',
                    500: '#FF6B2B',
                    600: '#E55A1F',
                    700: '#BF4A18',
                    800: '#993B13',
                    900: '#73290D',
                    950: '#3D1506',
                },
                surface: {
                    DEFAULT: '#FFFFFF',
                    elevated: '#F3F4F6',
                    overlay: 'rgba(0,0,0,0.05)',
                },
                background: '#F9FAFB',
                border: {
                    DEFAULT: '#E5E7EB',
                    subtle: '#F3F4F6',
                    hover: '#D1D5DB',
                },
                text: {
                    primary: '#111827',
                    secondary: '#374151',
                    muted: '#6B7280',
                    faint: '#9CA3AF',
                },
                accent: {
                    purple: '#7C3AED',
                    'purple-muted': '#6D28D9',
                },
                status: {
                    success: '#10B981',
                    warning: '#F59E0B',
                    error: '#EF4444',
                },
            },
            animation: {
                'fade-in': 'fadeIn 0.3s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
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
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(255, 107, 43, 0.1)' },
                    '100%': { boxShadow: '0 0 20px rgba(255, 107, 43, 0.15)' },
                },
            },
        },
    },
    plugins: [],
}
