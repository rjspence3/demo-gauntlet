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
                    50: '#FFF7ED',
                    100: '#FFEDD5',
                    200: '#FED7AA',
                    300: '#FDBA74',
                    400: '#FB923C',
                    500: '#F97316',
                    600: '#EA580C',
                    700: '#C2410C',
                    800: '#9A3412',
                    900: '#7C2D12',
                    950: '#431407',
                },
                ai: {
                    50: '#EEF2FF',
                    100: '#E0E7FF',
                    200: '#C7D2FE',
                    300: '#A5B4FC',
                    400: '#818CF8',
                    500: '#6366F1',
                    600: '#4F46E5',
                    700: '#4338CA',
                    800: '#3730A3',
                    900: '#312E81',
                },
                page: {
                    DEFAULT: '#F8F9FC',
                    alt: '#F1F3F8',
                },
                surface: {
                    DEFAULT: 'rgba(255, 255, 255, 0.85)',
                    solid: '#FFFFFF',
                    elevated: '#F3F4F6',
                    overlay: 'rgba(0, 0, 0, 0.04)',
                },
                border: {
                    DEFAULT: 'rgba(0, 0, 0, 0.08)',
                    subtle: 'rgba(0, 0, 0, 0.05)',
                    hover: 'rgba(0, 0, 0, 0.15)',
                    ai: 'rgba(99, 102, 241, 0.2)',
                },
                text: {
                    primary: '#0F1117',
                    secondary: '#374151',
                    muted: '#6B7280',
                    faint: '#9CA3AF',
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
                'soft-pulse': 'softPulse 2s ease-in-out infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(12px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
                softPulse: {
                    '0%, 100%': { opacity: '1' },
                    '50%': { opacity: '0.6' },
                },
            },
            boxShadow: {
                'glass': '0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04)',
                'glass-hover': '0 8px 32px rgba(0, 0, 0, 0.08), 0 2px 8px rgba(0, 0, 0, 0.04)',
                'ai-glow': '0 0 20px rgba(99, 102, 241, 0.1), 0 0 40px rgba(99, 102, 241, 0.05)',
            },
        },
    },
    plugins: [],
}
