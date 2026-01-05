# English-precis-challenge
English Precis Challenge is a web-based application that helps users practice and improve precis writing skills using AI-powered evaluation. It analyzes summaries for clarity, grammar, content relevance, and word limit adherence, providing instant feedback and scoring.
Précis Writing Challenge Website
A complete web application that evaluates user-written précis using AI models.

Project Structure
precis-challenge/
├── app.py              # Main Flask backend
├── models.py           # AI model implementations
├── data.py            # Sample paragraphs
├── requirements.txt    # Dependencies
├── templates/
│   └── index.html     # Frontend UI
├── static/
│   └── style.css      # Styling
└── README.md          # This file
Installation Steps
Create virtual environment:
python -m venv venv
venv\Scripts\activate  # Windows
Install dependencies:
pip install -r requirements.txt
Download required models (automatic on first run)
How to Run
Start the server:
python app_final.py
Open browser and go to: http://localhost:5000
How to Test
Click "Start Challenge" button
Read the generated paragraph
Write a précis in the text area
Click "Check Précis" to get your score
Scoring System
Semantic Similarity (0-3): How well your précis captures the meaning
AI Summary Comparison (0-4): Accuracy compared to AI-generated summary
Grammar Check (0-2): Grammar and language quality
Length Check (0-1): Appropriate length (25-50% of original)
Total Score: 0-10
Features
Random paragraph generation
Real-time AI evaluation
Detailed feedback
Clean, responsive UI
Production-ready code
Optional Enhancements
User Authentication: Add login/signup to track progress
Difficulty Levels: Easy/Medium/Hard paragraphs
Progress Tracking: Save scores and show improvement
More AI Models: Add additional evaluation criteria
Export Results: Download evaluation reports
Leaderboard: Compare scores with other users
Custom Paragraphs: Allow users to upload their own texts
Technical Details
Frontend: HTML/CSS/JavaScript (vanilla)
Backend: Python Flask
AI Models:
SBERT for semantic similarity
T5-small for summarization
LanguageTool for grammar checking
Deployment: Ready for cloud deployment (RENDER, AWS, etc.)
