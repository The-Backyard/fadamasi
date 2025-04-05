const gulp = require('gulp');
const nunjucksRender = require('gulp-nunjucks-render');
const gulpSass = require('gulp-sass');
const sass = require('sass');
const autoprefixer = require('gulp-autoprefixer');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const browserSync = require('browser-sync').create();
const imagemin = require('gulp-imagemin');
const del = require('del');
const concat = require('gulp-concat');
const rename = require('gulp-rename');
const plumber = require('gulp-plumber');
const sourcemaps = require('gulp-sourcemaps');
const fs = require('fs');
const path = require('path');

// File paths
const paths = {
    templates: {
        src: './src/templates/pages/**/*.njk',
        dest: './dist',
        watch: './src/templates/**/*.njk'
    },
    styles: {
        src: './src/styles/**/*.scss',
        dest: './dist/css'
    },
    scripts: {
        src: './src/scripts/**/*.js',
        dest: './dist/js'
    },
    images: {
        src: './src/images/**/*',
        dest: './dist/images'
    }
};

// Clean dist directory
function clean() {
    return del(['./dist/**/*']);
}

// Process templates
function templates() {
    // Gets .html and .njk files in pages
    return gulp.src(paths.templates.src)
        .pipe(plumber())
        // Render nunjucks templates
        .pipe(nunjucksRender({
            path: ['./src/templates']
        }))
        // Output files in dist folder
        .pipe(gulp.dest(paths.templates.dest))
        .pipe(browserSync.stream());
}

// Process Sass
const compileSass = gulpSass(sass); // Initialize gulp-sass with dart-sass

function styles() {
    return gulp.src(paths.styles.src)
        .pipe(plumber())
        .pipe(sourcemaps.init())
        .pipe(compileSass().on('error', compileSass.logError))
        .pipe(autoprefixer())
        .pipe(gulp.dest(paths.styles.dest))
        .pipe(cleanCSS())
        .pipe(rename({ suffix: '.min' }))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(paths.styles.dest))
        .pipe(browserSync.stream());
}

function copyAssets() {
    return gulp.src([
        './node_modules/bootstrap/dist/css/bootstrap.min.css',
        './node_modules/bootstrap/dist/js/bootstrap.bundle.min.js',
        './node_modules/@fortawesome/fontawesome-free/css/all.min.css',
        './node_modules/@fortawesome/fontawesome-free/webfonts/*',
        './node_modules/bootstrap-icons/font/bootstrap-icons.css',
        './node_modules/bootstrap-icons/font/fonts/bootstrap-icons.woff2',
        './node_modules/bootstrap-icons/font/fonts/bootstrap-icons.woff'
    ], { base: './node_modules' })
        .pipe(gulp.dest('./dist/vendor'));
}

// Process JavaScript
function scripts() {
    return gulp.src(paths.scripts.src)
        .pipe(plumber())
        .pipe(sourcemaps.init())
        .pipe(concat('main.js'))
        .pipe(gulp.dest(paths.scripts.dest))
        .pipe(uglify())
        .pipe(rename({ suffix: '.min' }))
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(paths.scripts.dest))
        .pipe(browserSync.stream());
}

// Optimize images
function images() {
    return gulp.src(paths.images.src)
        .pipe(imagemin())  // Just use default options for now
        .pipe(gulp.dest(paths.images.dest))
        .pipe(browserSync.stream());
}

// Copy static files
function copyStatic() {
    return gulp.src(['./src/favicon.ico', './src/robots.txt', './src/site.webmanifest'], { allowEmpty: true })
        .pipe(gulp.dest('./dist'));
}

// Watch files
function watch() {
    browserSync.init({
        server: {
            baseDir: './dist'
        },
        open: false
    });

    gulp.watch(paths.templates.watch, templates);
    gulp.watch(paths.styles.src, styles);
    gulp.watch(paths.scripts.src, scripts);
    gulp.watch(paths.images.src, images);
}

const build = gulp.series(clean, gulp.parallel(templates, styles, scripts, images, copyStatic, copyAssets));
const dev = gulp.series(build, watch);

// Export tasks
exports.templates = templates;
exports.styles = styles;
exports.scripts = scripts;
exports.images = images;
exports.clean = clean;
exports.build = build;
exports.watch = watch;
exports.dev = dev;
exports.default = dev;