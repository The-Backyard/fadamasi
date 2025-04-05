# Fadamasi UI Templates

This folder contains the static UI prototype for the Fadamasi Concept eCommerce platform.

Live Demo: [Fadamasi Concept](https://fadamasi.netlify.app)

## 🔮 Prerequisites

- Nodejs 18+
- npm 10+

## 📁 Folder Structure

```
prototype/
├── README.md
├── gulpfile.js              # Gulp task configuration
├── netlify.toml             # Netlify deployment config
├── package.json             # Project dependencies & scripts
└── src/                     # Source files
    ├── images/              # Static image assets
    ├── scripts/             # JS scripts for UI interaction
    ├── styles/              # Main CSS styles
    └── templates/           # Nunjucks template files
        ├── layouts/         # Base layout file(s)
        ├── macros/          # Nunjucks macros
        ├── modals/          # Modal components
        ├── pages/           # Complete HTML pages
        └── partials/        # Header, footer, etc.
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

### 3. Build for Production

```bash
npm run build
```

### 4. Clean Build Output

```bash
npm run clean
```

## 📦 Tech Stack

- Gulp 4
- Nunjucks
- Bootstrap 5
- Font Awesome & Bootstrap Icons

## 🌐 Deployment

The project is ready for deployment on Netlify. See `netlify.toml` for configuration.
