from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///precis_challenge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Score tracking model
class PrecisScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_score = db.Column(db.Float, nullable=False)
    semantic_score = db.Column(db.Float, nullable=False)
    ai_score = db.Column(db.Float, nullable=False)
    grammar_score = db.Column(db.Float, nullable=False)
    length_score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    user = db.relationship('User', backref=db.backref('scores', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make current_user available in templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

from paragraphs_data import SAMPLE_PARAGRAPHS

# Track used paragraphs per session
used_paragraphs = set()

# Simple evaluator
class SimplePrecisEvaluator:
    def evaluate_precis(self, original_text, precis_text):
        original_words = original_text.lower().split()
        precis_words = precis_text.lower().split()
        
        # Semantic similarity (basic word overlap)
        common_words = set(original_words) & set(precis_words)
        semantic_score = min(3.0, len(common_words) / len(set(original_words)) * 3)
        
        # AI comparison (simulate with keyword matching)
        key_phrases = self._extract_key_phrases(original_text)
        captured_phrases = sum(1 for phrase in key_phrases if phrase.lower() in precis_text.lower())
        ai_score = min(4.0, captured_phrases / max(len(key_phrases), 1) * 4)
        
        # Grammar check (basic)
        grammar_score = self._basic_grammar_check(precis_text)
        
        # Length check
        length_score = self._check_length(len(original_words), len(precis_words))
        
        total_score = semantic_score + ai_score + grammar_score + length_score
        
        feedback = self._generate_feedback(semantic_score, ai_score, grammar_score, length_score, len(original_words), len(precis_words))
        
        return {
            'total_score': round(total_score, 2),
            'semantic_score': round(semantic_score, 2),
            'ai_comparison_score': round(ai_score, 2),
            'grammar_score': round(grammar_score, 2),
            'length_score': round(length_score, 2),
            'feedback': feedback,
            'ai_summary': 'Professional text analysis completed successfully.'
        }
    
    def _extract_key_phrases(self, text):
        sentences = re.split(r'[.!?]+', text)
        key_phrases = []
        for sentence in sentences:
            words = sentence.strip().split()
            if len(words) > 3:
                key_phrases.append(' '.join(words[:4]))
        return key_phrases
    
    def _basic_grammar_check(self, text):
        issues = 0
        if not text.strip():
            return 0.0
        if not text[0].isupper():
            issues += 1
        if not text.strip()[-1] in '.!?':
            issues += 1
        if '  ' in text:
            issues += 1
        
        if issues == 0:
            return 2.0
        elif issues == 1:
            return 1.5
        elif issues == 2:
            return 1.0
        else:
            return 0.5
    
    def _check_length(self, original_words, precis_words):
        if precis_words == 0:
            return 0.0
        ratio = precis_words / original_words
        if 0.25 <= ratio <= 0.5:
            return 1.0
        elif 0.15 <= ratio < 0.25 or 0.5 < ratio <= 0.65:
            return 0.7
        elif 0.1 <= ratio < 0.15 or 0.65 < ratio <= 0.8:
            return 0.4
        else:
            return 0.1
    
    def _generate_feedback(self, semantic, ai_comp, grammar, length, orig_words, precis_words):
        feedback = []
        if semantic >= 2.0:
            feedback.append("[GOOD] Excellent word overlap with original text.")
        else:
            feedback.append("[IMPROVE] Include more key terms from the original.")
        
        if ai_comp >= 2.5:
            feedback.append("[GOOD] Key concepts well captured.")
        else:
            feedback.append("[IMPROVE] Focus on main ideas and key phrases.")
        
        if grammar >= 1.5:
            feedback.append("[GOOD] Grammar and structure look good.")
        else:
            feedback.append("[IMPROVE] Check capitalization and punctuation.")
        
        ratio = precis_words / orig_words if orig_words > 0 else 0
        if length >= 0.7:
            feedback.append("[GOOD] Appropriate length for a precis.")
        else:
            feedback.append(f"[IMPROVE] Aim for 25-50% of original length (currently {ratio:.1%}).")
        
        return " ".join(feedback)

evaluator = SimplePrecisEvaluator()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent scores for analytics
    recent_scores = PrecisScore.query.filter_by(user_id=current_user.id).order_by(PrecisScore.timestamp.desc()).limit(10).all()
    
    # Calculate statistics
    stats = {
        'total_attempts': len(current_user.scores),
        'avg_total_score': 0,
        'avg_semantic': 0,
        'avg_ai': 0,
        'avg_grammar': 0,
        'avg_length': 0,
        'skill_level': 'Beginner'
    }
    
    if current_user.scores:
        stats['avg_total_score'] = sum(s.total_score for s in current_user.scores) / len(current_user.scores)
        stats['avg_semantic'] = sum(s.semantic_score for s in current_user.scores) / len(current_user.scores)
        stats['avg_ai'] = sum(s.ai_score for s in current_user.scores) / len(current_user.scores)
        stats['avg_grammar'] = sum(s.grammar_score for s in current_user.scores) / len(current_user.scores)
        stats['avg_length'] = sum(s.length_score for s in current_user.scores) / len(current_user.scores)
        
        # Determine skill level
        if stats['avg_total_score'] >= 8.5:
            stats['skill_level'] = 'Expert'
        elif stats['avg_total_score'] >= 7.0:
            stats['skill_level'] = 'Advanced'
        elif stats['avg_total_score'] >= 5.5:
            stats['skill_level'] = 'Intermediate'
        else:
            stats['skill_level'] = 'Beginner'
    
    return render_template('dashboard.html', stats=stats, recent_scores=recent_scores)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/get_paragraph', methods=['POST'])
@login_required
def get_paragraph():
    try:
        global used_paragraphs
        
        # Reset if all paragraphs have been used
        if len(used_paragraphs) >= len(SAMPLE_PARAGRAPHS):
            used_paragraphs.clear()
        
        # Get unused paragraphs
        available_paragraphs = [p for i, p in enumerate(SAMPLE_PARAGRAPHS) if i not in used_paragraphs]
        
        # Select random paragraph from available ones
        paragraph = random.choice(available_paragraphs).strip()
        
        # Mark this paragraph as used
        paragraph_index = SAMPLE_PARAGRAPHS.index(paragraph)
        used_paragraphs.add(paragraph_index)
        
        return jsonify({
            'success': True,
            'paragraph': paragraph,
            'word_count': len(paragraph.split())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/evaluate_precis', methods=['POST'])
@login_required
def evaluate_precis():
    try:
        data = request.get_json()
        original_text = data.get('original_text', '').strip()
        precis_text = data.get('precis_text', '').strip()
        
        if not original_text or not precis_text:
            return jsonify({
                'success': False,
                'error': 'Both original text and precis are required'
            }), 400
        
        results = evaluator.evaluate_precis(original_text, precis_text)
        
        # Save score to database
        score = PrecisScore(
            user_id=current_user.id,
            total_score=results['total_score'],
            semantic_score=results['semantic_score'],
            ai_score=results['ai_comparison_score'],
            grammar_score=results['grammar_score'],
            length_score=results['length_score']
        )
        db.session.add(score)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Evaluation failed: {str(e)}'
        }), 500

@app.route('/clear_history', methods=['POST'])
@login_required
def clear_history():
    try:
        # Delete all scores for current user
        PrecisScore.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'History cleared successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("=== Precis Challenge Server ===")
    print("Server starting at: http://localhost:5000")
    print("Features: Login/Register, Dashboard, Contact")
    print("================================")
    app.run(debug=True, host='127.0.0.1', port=5000)