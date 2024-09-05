/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */

module.exports = {
    content: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /*
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',

        /*
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    safelist: [
        'bg-red-500', 'hover:bg-red-100', 'hover:bg-red-600', 'border-red-100',
        'bg-orange-500', 'hover:bg-orange-100', 'hover:bg-orange-600', 'border-orange-100',
        'bg-amber-500', 'hover:bg-amber-100', 'hover:bg-amber-600', 'border-amber-100',
        'bg-yellow-500', 'hover:bg-yellow-100', 'hover:bg-yellow-600', 'border-yellow-100',
        'bg-lime-500', 'hover:bg-lime-100', 'hover:bg-lime-600', 'border-lime-100',
        'bg-green-500', 'hover:bg-green-100', 'hover:bg-green-600', 'border-green-100',
        'bg-emerald-500', 'hover:bg-emerald-100', 'hover:bg-emerald-600', 'border-emerald-100',
        'bg-teal-500', 'hover:bg-teal-100', 'hover:bg-teal-600', 'border-teal-100',
        'bg-cyan-500', 'hover:bg-cyan-100', 'hover:bg-cyan-600', 'border-cyan-100',
        'bg-sky-500', 'hover:bg-sky-100', 'hover:bg-sky-600', 'border-sky-100',
        'bg-blue-500', 'hover:bg-blue-100', 'hover:bg-blue-600', 'border-blue-100',
        'bg-indigo-500', 'hover:bg-indigo-100', 'hover:bg-indigo-600', 'border-indigo-100',
        'bg-violet-500', 'hover:bg-violet-100', 'hover:bg-violet-600', 'border-violet-100',
        'bg-purple-500', 'hover:bg-purple-100', 'hover:bg-purple-600', 'border-purple-100',
        'bg-fuchsia-500', 'hover:bg-fuchsia-100', 'hover:bg-fuchsia-600', 'border-fuchsia-100',
        'bg-rose-500', 'hover:bg-rose-100', 'hover:bg-rose-600', 'border-rose-100',
    ],
    theme: {
        fontFamily: {
            'sans': ['Lato', 'sans-serif'],
        },
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
}
