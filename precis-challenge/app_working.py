from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import random
import re
from data import SAMPLE_PARAGRAPHS
from database import db, User, init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///precis_challenge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
init_db(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Make current_user available in templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

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
            'ai_summary': 'Basic text analysis completed. Upgrade to premium for full AI features.'
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
            feedback.append("[OK] Good word overlap with original text.")
        else:
            feedback.append("[IMPROVE] Try to include more key terms from the original.")
        
        if ai_comp >= 2.5:
            feedback.append("[OK] Key concepts well captured.")
        else:
            feedback.append("[IMPROVE] Focus on main ideas and key phrases.")
        
        if grammar >= 1.5:
            feedback.append("[OK] Basic grammar looks good.")
        else:
            feedback.append("[IMPROVE] Check capitalization and punctuation.")
        
        ratio = precis_words / orig_words if orig_words > 0 else 0
        if length >= 0.7:
            feedback.append("[OK] Good length for a précis.")
        else:
            feedback.append(f"[IMPROVE] Aim for 25-50% of original length (currently {ratio:.1%}).")
        
        return " ".join(feedback)

evaluator = SimplePrecisEvaluator()

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
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/get_paragraph', methods=['POST'])
@login_required
def get_paragraph():
    try:
        paragraph = random.choice(SAMPLE_PARAGRAPHS).strip()
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
                'error': 'Both original text and précis are required'
            }), 400
        
        results = evaluator.evaluate_precis(original_text, precis_text)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        print(f"Evaluation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Evaluation failed: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("Starting Précis Challenge Server...")
    print("Using basic text analysis (install AI dependencies for full features)")
    app.run(debug=True, host='0.0.0.0', port=5000)