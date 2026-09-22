# Student Guide

## Start a session

1. Run `streamlit run ui/app.py`.
2. Pick a **Course** and **Concept**.
3. Click **Start new session**.
4. Ask in English, Hindi, Bengali, Spanish, or mixed (e.g. Hinglish).

## What you see

- Detected language and intent under your message.
- Authorized scaffold tier, response language, and outcome under the buddy reply.
- **Sources used** expander when curriculum snippets were retrieved.
- Session panel: mastery, languages used, turn notes.

## How help is chosen

The buddy uses a fixed **Scaffold Map** (not a teacher toggle):

- Low mastery → richer scaffolds (up to what the Scaffold Map allows for your language).
- High mastery → lighter hints.
- Answer-hunting after switching languages → tightened help.

Mix languages freely for clarification. Asking for a full solution after being given a hint may be rewritten or blocked.
