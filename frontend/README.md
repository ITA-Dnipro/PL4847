# Forum Frontend

React (Vite) frontend for the Forum project.

## Requirements

- Node.js 18+ (recommended 20+)
- npm

## Setup

1. Install dependencies:

npm install

2. Create environment file from example:

copy .env.example .env

3. Start development server:

npm run dev

Open the URL shown in terminal (usually http://localhost:5173).

## Available Scripts

- npm run dev: Start Vite dev server
- npm run build: Build production files into dist/
- npm run preview: Preview production build locally
- npm run lint: Run ESLint

## Routes

- / : Home
- /login : Login
- /register : Register
- /startups/:id : Startup details page
- /dashboard : Investor dashboard
- /messages : Inbox

## API Base URL

Set API base URL in .env:

VITE_API_URL=http://localhost:8000