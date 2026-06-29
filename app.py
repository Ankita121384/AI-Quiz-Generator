import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_quiz(topic, difficulty, num_questions):
    prompt = f"""
Generate {num_questions} multiple choice questions about "{topic}" at {difficulty} difficulty level.

Return ONLY a JSON array in this exact format, nothing else:
[
  {{
    "question": "Question text here?",
    "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
    "answer": "A) Option 1",
    "explanation": "Brief explanation why this is correct"
  }}
]
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content

def parse_quiz(raw):
    try:
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

# ── App UI ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Quiz Generator", page_icon="🧠", layout="centered")
st.title("🧠 AI Quiz Generator")
st.markdown("Generate a **custom quiz** on any topic using AI!")
st.divider()

if "quiz" not in st.session_state:
    st.session_state.quiz = None
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

topic = st.text_input("📚 Enter a topic:", placeholder="e.g. Python, World History, AI, Math")
difficulty = st.selectbox("🎯 Select difficulty:", ["Easy", "Medium", "Hard"])
num_questions = st.slider("🔢 Number of questions:", min_value=3, max_value=10, value=5)

if st.button("✨ Generate Quiz", use_container_width=True):
    if not topic:
        st.warning("Please enter a topic!")
    else:
        with st.spinner("Generating your quiz... ⏳"):
            raw = generate_quiz(topic, difficulty, num_questions)
            quiz = parse_quiz(raw)
            if quiz:
                st.session_state.quiz = quiz
                st.session_state.answers = {}
                st.session_state.submitted = False
            else:
                st.error("Could not generate quiz. Please try again!")

if st.session_state.quiz:
    st.divider()
    st.subheader(f"📝 Your Quiz — {len(st.session_state.quiz)} Questions")

    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        selected = st.radio(
    f"Select answer for Q{i+1}:",
    [None] + q["options"],
    key=f"q_{i}",
    label_visibility="collapsed",
    format_func=lambda x: "Select an answer..." if x is None else x
)
        st.session_state.answers[i] = selected
        st.markdown("")

    if not st.session_state.submitted:
        if st.button("✅ Submit Quiz", use_container_width=True):
            st.session_state.submitted = True

    if st.session_state.submitted:
        st.divider()
        st.subheader("🏆 Results")
        score = 0
        for i, q in enumerate(st.session_state.quiz):
            user_ans = st.session_state.answers.get(i, "")
            correct = q["answer"]
            if user_ans == correct:
                score += 1
                st.success(f"✅ Q{i+1}: Correct! — {correct}")
            else:
                st.error(f"❌ Q{i+1}: Wrong! You chose: {user_ans} | Correct: {correct}")
            st.info(f"💡 {q['explanation']}")

        st.divider()
        percentage = int((score / len(st.session_state.quiz)) * 100)
        st.markdown(f"### 🎯 Your Score: {score}/{len(st.session_state.quiz)} ({percentage}%)")

        if percentage == 100:
            st.balloons()
            st.success("🏆 Perfect score! Outstanding!")
        elif percentage >= 70:
            st.success("🌟 Great job! Well done!")
        elif percentage >= 50:
            st.warning("📚 Good effort! Keep practicing!")
        else:
            st.error("💪 Keep studying! You'll do better next time!")

        if st.button("🔄 Try Another Quiz", use_container_width=True):
            st.session_state.quiz = None
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.rerun()

st.divider()
st.caption("Built with ❤️ using Python, Streamlit & Groq AI")