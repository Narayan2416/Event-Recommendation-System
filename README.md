# Event Recommendation System

A **web-based event recommendation platform** that helps users discover relevant events such as workshops, hackathons, seminars, and college activities.  
The system recommends events based on user searches, browsing behavior, and interaction history to provide a more personalized discovery experience.

---

## Features

### Semantic Event Search
Users can search for events using natural language queries.  
The system understands the meaning of the query and retrieves relevant events instead of relying only on keyword matching.

### Personalized Recommendations
The platform suggests events based on:
- Recent search queries
- User interactions such as views and clicks
- Popular events among other users

### Google Authentication
Users can securely sign in using **Google OAuth**, allowing quick access without creating a separate account.

### Interaction Tracking
User activities such as event views, clicks, and search queries are recorded to improve future recommendations.

### Similar Event Suggestions
When viewing an event, the system recommends other events that are similar.

### Admin Event Management
An admin interface allows new events to be added through an automated scraping module.

---

## Tech Stack

**Backend**
- Python
- Flask

**Machine Learning**
- Sentence Transformers
- Scikit-learn

**Database**
- MongoDB Atlas

**Frontend**
- HTML
- CSS
- JavaScript

**Authentication**
- Google OAuth 2.0

---

## Installation

### Clone the repository

```bash
git clone https://github.com/Narayan2416/Event-Recommendation-System.git
cd Event-Recommendation-System
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```
CLIENT_ID=your_google_client_id
FLASK_SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_connection_string
```

---

## Run the Application

```bash
python app.py
```


