const colors = require('tailwindcss/colors')

module.exports = {
    purge: [
        './templates/*.jinja',
        './templates/*.html',            
        './templates/*.jinja.html',
        './templates/*.css',
        './templates/*.jinja.css',
    ],
    darkMode: 'media', // or 'media' or 'class'
    theme: {
        screens: {
            md: '768px',
            lg: '1024px',
        },
        colors: {
            transparent: 'transparent',
            current: 'currentColor',
            black: colors.black,
            white: colors.white,
            gray: colors.coolGray,
            red: colors.red,
            yellow: colors.amber,
            green: colors.emerald,
            blue: colors.blue,
            indigo: colors.indigo,
            purple: colors.violet,
            pink: colors.pink,
        },
        container: {
            center: true,
        },
        borderRadius: {
            none: '0px',
            DEFAULT: '0.25rem',
            full: '50%'
        }
    },
    variants: {
        extend: {},
    },
    plugins: [],
}