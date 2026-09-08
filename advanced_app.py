# app.py - Simple Personality Mapper

import streamlit as st
import pandas as pd
import speech_recognition as sr
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import nltk

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('vader_lexicon', quiet=True)

# Page Config
st.set_page_config(
    page_title="🧠 Personality Mapper",
    page_icon="🧠",
    layout="wide"
)

# ========== CSS ==========
st.markdown("""
<style>
    .stApp {
        background-color: #f0f4ff;
    }
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown('<div class="main-header"><h1>🧠 Personality Mapper</h1><p>Analyze personality from text, voice, or files</p></div>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.header("📊 Features")
    
    feature = st.radio(
        "Choose Feature:",
        ["📝 Text Analysis", "📂 CSV Upload", "🎤 Voice Input", "🌐 Multilingual"]
    )
    
    st.divider()
    st.caption("Made with ❤️ using NLP")

# ========== PERSONALITY ANALYSIS ==========
def analyze_personality(text):
    words = text.lower().split()
    word_count = len(words)
    
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    
    positive_words = ['good', 'great', 'excellent', 'happy', 'love', 'wonderful', 'amazing', 
                     'enjoy', 'best', 'awesome', 'beautiful', 'nice', 'fantastic']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'sad', 'horrible', 'worst', 'angry',
                     'stupid', 'ugly', 'disgusting', 'frustrated']
    social_words = ['we', 'us', 'our', 'team', 'group', 'family', 'friends', 'together',
                   'community', 'share', 'help', 'support']
    anxiety_words = ['worry', 'stress', 'anxious', 'nervous', 'afraid', 'fear', 'scared',
                    'panic', 'tense', 'uncomfortable']
    
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    soc_count = sum(1 for w in words if w in social_words)
    anx_count = sum(1 for w in words if w in anxiety_words)
    
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
    
    return scores, type_code, sentiment, word_count

# ========== DISPLAY RESULTS - NO GRAPHS, ONLY TEXT BARS ==========
def display_results(scores, type_code, sentiment, word_count):
    st.subheader("📊 Personality Trait Scores")
    
    # Text bars - Like old style
    for trait, score in scores.items():
        bar = "█" * int(score/10) + "░" * (10 - int(score/10))
        if score > 70:
            level = "🔵 High"
        elif score < 40:
            level = "🔴 Low"
        else:
            level = "🟡 Moderate"
        st.write(f"{trait:20} | {bar} {score:.1f}% ({level})")
    
    # Personality Type
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
                padding: 15px; border-radius: 10px; color: white; text-align: center;">
        <div style="font-size: 36px; font-weight: bold;">{type_code}</div>
        <div style="font-size: 16px; opacity: 0.9;">{type_name}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📝 Word Count", word_count)
    with col2:
        st.metric("💬 Sentiment", f"{sentiment['compound']:.2f}")

# ========== TRANSLATION ==========
def translate_text(text, dest_lang):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=dest_lang)
        return translation.text
    except:
        return None

# ========== FEATURE 1: TEXT ANALYSIS ==========
if feature == "📝 Text Analysis":
    st.subheader("📝 Enter Text for Analysis")
    
    text = st.text_area(
        "Type your text here:",
        height=150,
        placeholder="Example: I love traveling and meeting new people..."
    )
    
    if st.button("🔍 Analyze", type="primary"):
        if text:
            with st.spinner("Analyzing..."):
                scores, type_code, sentiment, word_count = analyze_personality(text)
                display_results(scores, type_code, sentiment, word_count)
                
                if 'history' not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({
                    'text': text[:100],
                    'type': type_code
                })
        else:
            st.warning("⚠️ Please enter some text!")

# ========== FEATURE 2: CSV UPLOAD ==========
elif feature == "📂 CSV Upload":
    st.subheader("📂 Upload CSV File")
    
    st.info("CSV must have a 'text' column")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        if 'text' not in df.columns:
            st.error("CSV must have a 'text' column!")
        else:
            st.write(f"📊 Found {len(df)} texts")
            
            if st.button("🚀 Analyze All", type="primary"):
                results = []
                progress_bar = st.progress(0)
                
                for idx, row in df.iterrows():
                    text = str(row['text'])
                    if text and text != 'nan':
                        scores, type_code, _, _ = analyze_personality(text)
                        results.append({
                            'text': text[:50] + '...',
                            'Openness': round(scores['Openness'], 1),
                            'Conscientiousness': round(scores['Conscientiousness'], 1),
                            'Extraversion': round(scores['Extraversion'], 1),
                            'Agreeableness': round(scores['Agreeableness'], 1),
                            'Neuroticism': round(scores['Neuroticism'], 1),
                            'Type': type_code
                        })
                    progress_bar.progress((idx + 1) / len(df))
                
                results_df = pd.DataFrame(results)
                st.success(f"✅ Analyzed {len(results)} texts!")
                st.dataframe(results_df)
                
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="results.csv",
                    mime="text/csv"
                )

# ========== FEATURE 3: VOICE INPUT ==========
elif feature == "🎤 Voice Input":
    st.subheader("🎤 Speech to Text - Voice Input")
    
    st.info("Click 'Start Recording' and speak clearly")
    audio_value = st.audio_input("🎙️ Record your voice")

if audio_value is not None:
    try:
        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_value) as source:
            audio = recognizer.record(source)

        with st.spinner("🔄 Transcribing..."):
            text = recognizer.recognize_google(audio)

        st.success(f"✅ Transcribed: {text}")
        st.session_state['voice_text'] = text

    except sr.UnknownValueError:
        st.error("Could not understand audio. Please try again.")

    except sr.RequestError:
        st.error("Network error. Check your internet connection.")

    except Exception as e:
        st.error(f"Error: {e}")
    
    if 'voice_text' in st.session_state:
        text = st.session_state['voice_text']
        st.text_area("📝 Transcribed Text:", text, height=100)
        
        if st.button("🔍 Analyze Voice Text", type="primary"):
            scores, type_code, sentiment, word_count = analyze_personality(text)
            display_results(scores, type_code, sentiment, word_count)

# ========== FEATURE 4: MULTILINGUAL ==========
elif feature == "🌐 Multilingual":
    st.subheader("🌐 Translate and Analyze")
    
    lang_map = {
        'Tamil': 'ta',
        'Hindi': 'hi',
        'English': 'en',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de'
    }
    
    input_lang = st.selectbox("Input Language", list(lang_map.keys()))
    output_lang = st.selectbox("Translate to", ['English', 'Tamil', 'Hindi', 'Spanish', 'French', 'German'])
    
    text = st.text_area(
        f"Enter text in {input_lang}:",
        height=150,
        placeholder="Type your text here..."
    )
    
    if st.button("🌐 Translate & Analyze", type="primary"):
        if text:
            try:
                translator = Translator()
                
                with st.spinner("Translating..."):
                    # Translate to English
                    if input_lang != 'English':
                        english_text = GoogleTranslator(source=lang_map[input_lang],target='en').translate(text)
                        st.success(f"📝 Translated to English: {english_text}")
                    else:
                        english_text = text
                        st.info("📝 Already in English")
                    
                    # Translate to output language
                    if output_lang != 'English':
                        dest_lang = lang_map[output_lang]
                        display_translation = GoogleTranslator(source='en',target=dest_lang).translate(english_text)
                        st.markdown(f"### 📝 {output_lang} Translation:")
                        st.write(display_translation)
                    else:
                        st.markdown("### 📝 English Text:")
                        st.write(english_text)
                    
                    st.write("---")
                    
                    # Analyze personality
                    scores, type_code, sentiment, word_count = analyze_personality(english_text)
                    display_results(scores, type_code, sentiment, word_count)
                    
            except Exception as e:
                st.error(f"Translation error: {e}")
        else:
            st.warning("Please enter text!")

# ========== HISTORY ==========
st.write("---")
st.write("### 📜 Analysis History")

if 'history' in st.session_state and st.session_state.history:
    for i, item in enumerate(st.session_state.history[-5:]):
        st.write(f"**{i+1}.** {item['text']}... → Type: {item['type']}")
else:
    st.caption("No history yet. Analyze some text!")

# ========== FOOTER ==========
st.write("---")
st.caption("🧠 Personality Mapper • Built with NLP • Voice Input • CSV Upload • Translation")
