# main.py - Full code paste pannunga

import re
import nltk
import spacy
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np

# Download NLTK data (first time only)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')

# Load spacy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    print("Please run: python -m spacy download en_core_web_sm")

class PersonalityMapper:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.positive_words = set(['good', 'great', 'excellent', 'happy', 'love', 'wonderful'])
        self.negative_words = set(['bad', 'terrible', 'awful', 'hate', 'sad', 'horrible'])
        self.cognitive_words = set(['think', 'know', 'believe', 'consider', 'understand'])
        self.social_words = set(['we', 'us', 'our', 'team', 'group', 'family', 'friends'])
        self.anxiety_words = set(['worry', 'stress', 'anxious', 'nervous', 'afraid', 'fear'])
    
    def predict_personality(self, text):
        """Simple rule-based personality prediction"""
        
        # Clean text
        text = text.lower()
        words = text.split()
        word_count = len(words)
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.polarity_scores(text)
        blob = TextBlob(text)
        
        # Count word categories
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        cog_count = sum(1 for w in words if w in self.cognitive_words)
        soc_count = sum(1 for w in words if w in self.social_words)
        anx_count = sum(1 for w in words if w in self.anxiety_words)
        
        # Calculate scores (0-100)
        openness = 50 + (cog_count / (word_count + 1)) * 100 + (sentiment['pos'] * 30)
        conscientiousness = 50 + (1 - (neg_count / (word_count + 1))) * 50
        extraversion = 50 + (soc_count / (word_count + 1)) * 100 + (sentiment['pos'] * 20)
        agreeableness = 50 + (sentiment['compound'] * 50) - (neg_count / (word_count + 1)) * 30
        neuroticism = 50 + (anx_count / (word_count + 1)) * 150 - (sentiment['pos'] * 20)
        
        # Clamp between 0-100
        scores = {
            'Openness': max(0, min(100, openness)),
            'Conscientiousness': max(0, min(100, conscientiousness)),
            'Extraversion': max(0, min(100, extraversion)),
            'Agreeableness': max(0, min(100, agreeableness)),
            'Neuroticism': max(0, min(100, neuroticism))
        }
        
        return scores
    
    def get_description(self, scores):
        """Get personality description"""
        desc = {}
        
        for trait, score in scores.items():
            if score > 70:
                level = "High"
            elif score < 40:
                level = "Low"
            else:
                level = "Moderate"
            
            if trait == 'Openness':
                desc[trait] = f"{level} - {'Creative, curious' if level == 'High' else 'Practical, routine' if level == 'Low' else 'Balanced'}"
            elif trait == 'Conscientiousness':
                desc[trait] = f"{level} - {'Organized, reliable' if level == 'High' else 'Spontaneous, flexible' if level == 'Low' else 'Balanced'}"
            elif trait == 'Extraversion':
                desc[trait] = f"{level} - {'Outgoing, energetic' if level == 'High' else 'Reserved, quiet' if level == 'Low' else 'Balanced'}"
            elif trait == 'Agreeableness':
                desc[trait] = f"{level} - {'Compassionate, cooperative' if level == 'High' else 'Competitive, skeptical' if level == 'Low' else 'Balanced'}"
            elif trait == 'Neuroticism':
                desc[trait] = f"{level} - {'Anxious, sensitive' if level == 'High' else 'Emotionally stable' if level == 'Low' else 'Balanced'}"
        
        return desc

# ===== MAIN PROGRAM =====
if __name__ == "__main__":
    print("=" * 60)
    print("🧠 PERSONALITY MAPPER")
    print("=" * 60)
    
    # Create object
    mapper = PersonalityMapper()
    
    # Sample text
    text = """I absolutely love learning new things and exploring different cultures. 
    I'm an outgoing person who enjoys meeting new people and making friends. 
    Sometimes I worry too much about the future, but I try to stay organized and plan ahead."""
    
    print("\n📝 Text to analyze:")
    print("-" * 40)
    print(text)
    print("-" * 40)
    
    # Predict
    scores = mapper.predict_personality(text)
    descriptions = mapper.get_description(scores)
    
    print("\n📊 PERSONALITY TRAIT SCORES:")
    print("-" * 40)
    
    for trait, score in scores.items():
        bar = "█" * int(score/10) + "░" * (10 - int(score/10))
        print(f"{trait:20} | {bar} {score:.1f}%")
        print(f"   {descriptions[trait]}")
        print()
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")