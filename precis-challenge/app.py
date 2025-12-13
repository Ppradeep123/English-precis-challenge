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

# Make current_user available in templates
@app.context_processor
def inject_user():
    return dict(current_user=current_user)

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Sample paragraphs
SAMPLE_PARAGRAPHS = [
    """
    Climate change represents one of the most pressing challenges of our time, with far-reaching consequences for ecosystems, human societies, and the global economy. Rising temperatures, melting ice caps, and extreme weather events are becoming increasingly common, disrupting agricultural patterns and threatening food security worldwide. The scientific consensus is clear: human activities, particularly the burning of fossil fuels and deforestation, are the primary drivers of these changes. Immediate action is required to reduce greenhouse gas emissions, transition to renewable energy sources, and implement sustainable practices across all sectors of society. Without decisive intervention, the consequences will become increasingly severe and irreversible.
    """,
    """
    The digital revolution has fundamentally transformed how we communicate, work, and access information. Social media platforms have connected billions of people across the globe, enabling instant communication and the rapid spread of ideas. However, this connectivity comes with significant challenges, including privacy concerns, misinformation, and the potential for social manipulation. The rise of artificial intelligence and automation is reshaping industries, creating new opportunities while simultaneously displacing traditional jobs. As we navigate this digital landscape, it is crucial to develop policies and frameworks that harness the benefits of technology while mitigating its risks and ensuring equitable access for all members of society.
    """,
    """
    Education systems worldwide are undergoing significant transformation as they adapt to the demands of the 21st century. Traditional teaching methods are being supplemented or replaced by innovative approaches that emphasize critical thinking, creativity, and collaboration. Technology integration in classrooms has accelerated, particularly following the global pandemic, which demonstrated both the potential and limitations of remote learning. Educators are increasingly recognizing the importance of personalized learning experiences that cater to diverse learning styles and abilities. The challenge lies in preparing students not just with knowledge, but with the skills necessary to thrive in an rapidly evolving world where adaptability and lifelong learning are essential.
    """
]

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
                'error': 'Both original text and precis are required'
            }), 400
        
        results = evaluator.evaluate_precis(original_text, precis_text)
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Evaluation failed: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Starting Precis Challenge Server...")
    print("Server will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)