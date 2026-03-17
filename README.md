# CineMatch — AI Movie Recommender

An AI-powered movie recommendation system covering Hollywood, Bollywood, Tollywood, Korean cinema, and more.

## Setup

### 1. Install dependencies
```bash
npm install
```

### 2. Add your Anthropic API key
Copy `.env.example` to `.env` and add your key:
```bash
cp .env.example .env
```
Then edit `.env`:
```
VITE_ANTHROPIC_API_KEY=your_api_key_here
```
Get your API key at: https://console.anthropic.com/

### 3. Run the app
```bash
npm run dev
```
Open http://localhost:5173 in your browser.

## Build for production
```bash
npm run build
npm run preview
```

## Features
- Search any movie from any industry
- Get 8 AI-powered similar movie recommendations
- Filter by Hollywood, Bollywood, Tollywood, Korean, World Cinema
- Match score and reason for each recommendation
- Quick-pick popular movies
