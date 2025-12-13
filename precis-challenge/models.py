import numpy as np
try:
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    import language_tool_python
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    exit(1)

class PrecisEvaluator:
    def __init__(self):
        """Initialize all AI models for evaluation"""
        try:
            print("Loading semantic similarity model...")
            self.similarity_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
            
            print("Loading summarization model...")
            self.summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
            
            print("Loading grammar checker...")
            self.grammar_tool = language_tool_python.LanguageTool('en-US')
            print("All models loaded successfully!")
        except Exception as e:
            print(f"Error loading models: {e}")
            raise
    
    def calculate_semantic_similarity(self, original_text, precis_text):
        """Calculate semantic similarity score (0-3)"""
        try:
            # Generate embeddings
            original_embedding = self.similarity_model.encode([original_text])
            precis_embedding = self.similarity_model.encode([precis_text])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(original_embedding, precis_embedding)[0][0]
            
            # Convert to 0-3 scale
            score = min(3.0, max(0.0, similarity * 3))
            return round(score, 2)
        except Exception as e:
            print(f"Semantic similarity error: {e}")
            return 1.5  # Default score
    
    def compare_with_ai_summary(self, original_text, precis_text):
        """Compare précis with AI-generated summary (0-4)"""
        try:
            # Generate AI summary
            max_length = min(150, len(original_text.split()) // 2)
            min_length = max(30, max_length // 3)
            
            ai_summary = self.summarizer(
                original_text, 
                max_length=max_length, 
                min_length=min_length, 
                do_sample=False
            )[0]['summary_text']
            
            # Compare précis with AI summary
            ai_embedding = self.similarity_model.encode([ai_summary])
            precis_embedding = self.similarity_model.encode([precis_text])
            
            similarity = cosine_similarity(ai_embedding, precis_embedding)[0][0]
            
            # Convert to 0-4 scale
            score = min(4.0, max(0.0, similarity * 4))
            return round(score, 2), ai_summary
        except Exception as e:
            print(f"AI summary comparison error: {e}")
            return 2.0, "AI summary unavailable"
    
    def check_grammar(self, text):
        """Check grammar and return score (0-2)"""
        try:
            matches = self.grammar_tool.check(text)
            error_count = len(matches)
            
            # Score based on error density
            word_count = len(text.split())
            error_ratio = error_count / max(word_count, 1)
            
            if error_ratio <= 0.02:  # Less than 2% errors
                score = 2.0
            elif error_ratio <= 0.05:  # Less than 5% errors
                score = 1.5
            elif error_ratio <= 0.1:   # Less than 10% errors
                score = 1.0
            else:
                score = 0.5
            
            return score, error_count
        except Exception as e:
            print(f"Grammar check error: {e}")
            return 1.0, 0
    
    def check_length(self, original_text, precis_text):
        """Check if précis length is appropriate (0-1)"""
        original_words = len(original_text.split())
        precis_words = len(precis_text.split())
        
        if precis_words == 0:
            return 0.0
        
        ratio = precis_words / original_words
        
        # Ideal ratio is 25-50% of original
        if 0.25 <= ratio <= 0.5:
            score = 1.0
        elif 0.15 <= ratio < 0.25 or 0.5 < ratio <= 0.65:
            score = 0.7
        elif 0.1 <= ratio < 0.15 or 0.65 < ratio <= 0.8:
            score = 0.4
        else:
            score = 0.1
        
        return score
    
    def evaluate_precis(self, original_text, precis_text):
        """Complete evaluation of précis"""
        # Clean texts
        original_text = original_text.strip()
        precis_text = precis_text.strip()
        
        if not precis_text:
            return {
                'total_score': 0,
                'semantic_score': 0,
                'ai_comparison_score': 0,
                'grammar_score': 0,
                'length_score': 0,
                'feedback': 'Please write a précis to evaluate.',
                'ai_summary': ''
            }
        
        # Calculate all scores
        semantic_score = self.calculate_semantic_similarity(original_text, precis_text)
        ai_score, ai_summary = self.compare_with_ai_summary(original_text, precis_text)
        grammar_score, error_count = self.check_grammar(precis_text)
        length_score = self.check_length(original_text, precis_text)
        
        # Calculate total score
        total_score = semantic_score + ai_score + grammar_score + length_score
        
        # Generate feedback
        feedback = self._generate_feedback(
            semantic_score, ai_score, grammar_score, length_score, 
            error_count, len(original_text.split()), len(precis_text.split())
        )
        
        return {
            'total_score': round(total_score, 2),
            'semantic_score': semantic_score,
            'ai_comparison_score': ai_score,
            'grammar_score': grammar_score,
            'length_score': length_score,
            'feedback': feedback,
            'ai_summary': ai_summary
        }
    
    def _generate_feedback(self, semantic, ai_comp, grammar, length, errors, orig_words, precis_words):
        """Generate detailed feedback"""
        feedback = []
        
        # Semantic feedback
        if semantic >= 2.5:
            feedback.append("✓ Excellent semantic similarity - you captured the main ideas well.")
        elif semantic >= 1.5:
            feedback.append("• Good semantic similarity - most key points captured.")
        else:
            feedback.append("✗ Low semantic similarity - focus on capturing the main ideas.")
        
        # AI comparison feedback
        if ai_comp >= 3.0:
            feedback.append("✓ Your précis aligns well with AI analysis.")
        elif ai_comp >= 2.0:
            feedback.append("• Decent alignment with AI analysis.")
        else:
            feedback.append("✗ Consider improving accuracy and completeness.")
        
        # Grammar feedback
        if grammar >= 1.5:
            feedback.append("✓ Good grammar and language quality.")
        else:
            feedback.append(f"✗ Grammar needs improvement ({errors} errors found).")
        
        # Length feedback
        ratio = precis_words / orig_words if orig_words > 0 else 0
        if length >= 0.7:
            feedback.append("✓ Appropriate length for a précis.")
        else:
            feedback.append(f"✗ Length issue - aim for 25-50% of original ({precis_words}/{orig_words} words = {ratio:.1%}).")
        
        return " ".join(feedback)