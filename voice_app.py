# voice_app.py - Simple Personality Mapper with Voice Input

import streamlit as st
import speech_recognition as sr
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('vader_lexicon', quiet=True)

# Page Config - Simple White Background
st.set_page_config(
    page_title="🧠 Personality Mapper",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS - Clean White Background
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .stApp {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🧠 Personality Mapper</h1><p>Analyze your personality from text or voice</p></div>', unsafe_allow_html=True)

# ========== SIDEBAR - Simple Features ==========
with st.sidebar:
    st.header("📝 Choose Input Method")
    
    option = st.radio(
        "Select:",
        ["✏️ Type Text", "🎤 Voice Input"]
    )
    
    st.divider()
    st.caption("💡 Tip: Speak clearly for voice input")

# ========== PERSONALITY ANALYSIS FUNCTION ==========
def analyze_personality(text):
    """Simple personality analysis"""
    words = text.lower().split()
    word_count = len(words)
    
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    
    # Keywords
    positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'wonderful', 'amazing', 
                     'enjoy', 'best', 'awesome', 'beautiful', 'nice', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'horrible', 'worst', 'angry']
    social_words = ['we', 'us', 'our', 'team', 'group', 'family', 'friends', 'together']
    anxiety_words = ['worry', 'stress', 'anxious', 'nervous', 'afraid', 'fear', 'scared']
    
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    soc_count = sum(1 for w in words if w in social_words)
    anx_count = sum(1 for w in words if w in anxiety_words)
    
    # Calculate scores
    openness = 50 + (len(set(words)) / (word_count + 1) * 40)
    conscientiousness = 50 + (1 - neg_count/(word_count+1)) * 50
    extraversion = 50 + (soc_count/(word_count+1)) * 100 + sentiment['pos'] * 40
    agreeableness = 50 + sentiment['compound'] * 50 - (neg_count/(word_count+1)) * 30
    neuroticism = 50 + (anx_count/(word_count+1)) * 150 - sentiment['pos'] * 30
    
    scores = {
        'Openness': max(0, min(100, openness)),
        'Conscientiousness': max(0, min(100, conscientiousness)),
        'Extraversion': max(0, min(100, extraversion)),
        'Agreeableness': max(0, min(100, agreeableness)),
        'Neuroticism': max(0, min(100, neuroticism))
    }
    
    # Personality Type
    type_code = ""
    type_code += "E" if scores['Extraversion'] > 50 else "I"
    type_code += "S" if scores['Conscientiousness'] > 50 else "N"
    type_code += "F" if scores['Agreeableness'] > 50 else "T"
    type_code += "J" if scores['Conscientiousness'] > 50 else "P"
    
    return scores, type_code, word_count

# ========== DISPLAY RESULTS ==========
def display_results(scores, type_code, word_count):
    """Show results in simple format"""
    
    st.subheader("📊 Personality Trait Scores")
    
    # Display each trait with progress bar
    for trait, score in scores.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{trait}**")
        with col2:
            # Color based on score
            if score > 70:
                color = "green"
                level = "🔵 High"
            elif score > 40:
                color = "orange"
                level = "🟡 Moderate"
            else:
                color = "red"
                level = "🔴 Low"
            st.progress(score/100)
            st.caption(f"{score:.1f}% - {level}")
    
    # Personality Type
    st.subheader("📝 Your Personality Type")
    
    type_names = {
        'ENFJ': 'The Protagonist', 'ENFP': 'The Campaigner',
        'ENTJ': 'The Commander', 'ENTP': 'The Debater',
        'ESFJ': 'The Consul', 'ESFP': 'The Entertainer',
        'ESTJ': 'The Executive', 'ESTP': 'The Entrepreneur',
        'INFJ': 'The Advocate', 'INFP': 'The Mediator',
        'INTJ': 'The Architect', 'INTP': 'The Logician',
        'ISFJ': 'The Defender', 'ISFP': 'The Adventurer',
        'ISTJ': 'The Logistician', 'ISTP': 'The Virtuoso'
    }
    
    type_name = type_names.get(type_code, "Balanced Type")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px; border-radius: 15px; color: white; text-align: center;">
        <div style="font-size: 48px; font-weight: bold;">{type_code}</div>
        <div style="font-size: 18px; opacity: 0.9;">{type_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.metric("📝 Word Count", word_count)

# ========== FEATURE 1: TYPE TEXT ==========
if option == "✏️ Type Text":
    st.subheader("✏️ Enter Your Text")
    
    text = st.text_area(
        "Type your text here:",
        height=150,
        placeholder="Example: I love traveling and meeting new people..."
    )
    
    if st.button("🔍 Analyze", type="primary"):
        if text:
            with st.spinner("Analyzing..."):
                scores, type_code, word_count = analyze_personality(text)
                display_results(scores, type_code, word_count)
        else:
            st.warning("⚠️ Please enter some text!")

# ========== FEATURE 2: VOICE INPUT ==========
elif option == "🎤 Voice Input":
    st.subheader("🎤 Speak into Your Microphone")
    
    st.info("""
    **How to use:**
    1. Click **"Start Recording"** button below
    2. Speak clearly into your microphone
    3. Wait for transcription
    4. Click **"Analyze"** to see results
    """)
    
    # Record button
    if st.button("🎙️ Start Recording", type="primary"):
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.write("🔴 **Recording... Please speak clearly**")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)
                
            with st.spinner("🔄 Transcribing your speech..."):
                text = recognizer.recognize_google(audio)
                st.success(f"✅ **Transcribed:** {text}")
                
                # Store in session
                st.session_state['voice_text'] = text
                
        except sr.WaitTimeoutError:
            st.error("⏰ No speech detected. Please try again.")
        except sr.UnknownValueError:
            st.error("🔇 Could not understand audio. Please speak clearly and try again.")
        except sr.RequestError:
            st.error("🌐 Network error. Check your internet connection.")
        except Exception as e:
            st.error(f"❌ Error: {e}. Please check your microphone.")
    
    # Show transcribed text and analyze
    if 'voice_text' in st.session_state:
        text = st.session_state['voice_text']
        
        st.subheader("📝 Transcribed Text")
        st.write(f"**{text}**")
        
        if st.button("🔍 Analyze Voice Text", type="primary"):
            with st.spinner("Analyzing..."):
                scores, type_code, word_count = analyze_personality(text)
                display_results(scores, type_code, word_count)

# ========== FOOTER ==========
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🧠 Personality Mapper")
with col2:
    st.caption("🔬 NLP Powered")
with col3:
    st.caption("🎤 Voice Input Supported")