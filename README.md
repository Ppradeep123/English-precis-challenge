# Précis Writing Challenge Website

A complete web application that evaluates user-written précis using AI models.

## Project Structure
```
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
```

## Installation Steps

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required models (automatic on first run)

## How to Run

1. Start the server:
```bash
python app_final.py
```

2. Open browser and go to: `http://localhost:5000`

## How to Test

1. Click "Start Challenge" button
2. Read the generated paragraph
3. Write a précis in the text area
4. Click "Check Précis" to get your score

## Scoring System

- **Semantic Similarity (0-3)**: How well your précis captures the meaning
- **AI Summary Comparison (0-4)**: Accuracy compared to AI-generated summary  
- **Grammar Check (0-2)**: Grammar and language quality
- **Length Check (0-1)**: Appropriate length (25-50% of original)
- **Total Score: 0-10**

## Features

- Random paragraph generation
- Real-time AI evaluation
- Detailed feedback
- Clean, responsive UI
- Production-ready code

## Optional Enhancements

1. **User Authentication**: Add login/signup to track progress
2. **Difficulty Levels**: Easy/Medium/Hard paragraphs
3. **Progress Tracking**: Save scores and show improvement
4. **More AI Models**: Add additional evaluation criteria
5. **Export Results**: Download evaluation reports
6. **Leaderboard**: Compare scores with other users
7. **Custom Paragraphs**: Allow users to upload their own texts

## Technical Details

- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Backend**: Python Flask
- **AI Models**: 
  - SBERT for semantic similarity
  - T5-small for summarization
  - LanguageTool for grammar checking
- **Deployment**: Ready for cloud deployment (Heroku, AWS, etc.)

## Troubleshooting

- **Slow first load**: AI models download on first use
- **Memory issues**: Reduce model sizes in models.py
- **Port conflicts**: Change port in app.py
- **Grammar tool errors**: Install Java for LanguageTool
