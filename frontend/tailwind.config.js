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
                    50: '#E6F1FB',
                    100: '#CCE4F7',
                    200: '#99C9EF',
                    300: '#66ADE7',
                    400: '#3392DF',
                    500: '#0176D3',
                    600: '#0264B0',
                    700: '#014D89',
                    800: '#013762',
                    900: '#00203B',
                    950: '#001525',
                },
                ai: {
                    50: 'rgba(1, 118, 211, 0.08)',
                    100: 'rgba(1, 118, 211, 0.15)',
                    200: 'rgba(1, 118, 211, 0.25)',
                    300: 'rgba(1, 118, 211, 0.4)',
                    400: '#3392DF',
                    500: '#0176D3',
                    600: '#0264B0',
                    700: '#014D89',
                    800: '#013762',
                    900: '#00203B',
                },
                page: {
                    DEFAULT: '#002E50',
                    alt: '#032D60',
                },
                surface: {
                    DEFAULT: 'rgba(10, 61, 107, 0.9)',
                    solid: '#0A3D6B',
                    elevated: '#0D4A7F',
                    overlay: 'rgba(0, 0, 0, 0.3)',
                },
                border: {
                    DEFAULT: 'rgba(255, 255, 255, 0.12)',
                    subtle: 'rgba(255, 255, 255, 0.06)',
                    hover: 'rgba(255, 255, 255, 0.2)',
                    ai: 'rgba(1, 118, 211, 0.25)',
                },
                text: {
                    primary: '#FFFFFF',
                    secondary: 'rgba(255, 255, 255, 0.85)',
                    muted: 'rgba(255, 255, 255, 0.6)',
                    faint: 'rgba(255, 255, 255, 0.4)',
                },
                status: {
                    success: '#2E844A',
                    warning: '#FE9339',
                    error: '#BA0517',
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
                'glass': '0 4px 24px rgba(0, 0, 0, 0.3), 0 1px 4px rgba(0, 0, 0, 0.2)',
                'glass-hover': '0 8px 32px rgba(0, 0, 0, 0.4), 0 2px 8px rgba(0, 0, 0, 0.2)',
                'ai-glow': '0 0 20px rgba(1, 118, 211, 0.15), 0 0 40px rgba(1, 118, 211, 0.08)',
            },
        },
    },
    plugins: [],
}
