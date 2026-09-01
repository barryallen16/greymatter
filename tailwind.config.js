/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.html","./archive/*.html","./roadmaps/*.html"],
  theme: { extend: { fontFamily: { sans: ['Geist','Inter','ui-sans-serif','system-ui'], mono: ['Geist Mono','monospace'], pixel: ['GeistPixel','Geist','sans-serif'] } } },
  plugins: [require('@tailwindcss/typography')],
}
