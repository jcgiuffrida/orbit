# Orbit

A personal family app for tracking people and conversations in a social orbit. (Not a public app)

## Overview

Orbit helps maintain meaningful connections by tracking:
- **People**: Contact info, birthdays, how you met, and AI-generated summaries
- **Conversations**: Notes from interactions, including group conversations
- **Contact Attempts**: Log when you reach out via text, email, calls, etc.
- **Relationships**: Map connections between people in your network

## Models

- **Person**: Core contact information and notes
- **Conversation**: Group conversations with participants, date, type, location, and notes
- **ContactAttempt**: Outreach tracking that can optionally link to resulting conversations
- **Relationship**: Links between people (partner, family, friend, colleague, etc.)

## Setup

1. Activate virtual environment
2. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

4. Run development server:
   ```bash
   python manage.py runserver
   ```

## Tech Stack

- **Backend**: Django 5.2.5
- **Frontend**: Vue.js
- **Database**: SQLite