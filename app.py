import streamlit as st
import PyPDF2
import io
import time
from src.llama_quiz_generator import QuizGenerator
from gtts import gTTS
import os

st.set_page_config(
    page_title="PDF2Prep",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'quiz' not in st.session_state:
    st.session_state.quiz = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'question_count' not in st.session_state:
    st.session_state.question_count = 5
if 'quiz_start_time' not in st.session_state:
    st.session_state.quiz_start_time = None
if 'quiz_end_time' not in st.session_state:
    st.session_state.quiz_end_time = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'pdf_text' not in st.session_state:
    st.session_state.pdf_text = ""
if 'personal_notes' not in st.session_state:
    st.session_state.personal_notes = ""
if 'concept_topics' not in st.session_state:
    st.session_state.concept_topics = []
if 'concept_summaries' not in st.session_state:
    st.session_state.concept_summaries = {}

quiz_generator = QuizGenerator()

def get_topic_summary(topic, pdf_text):
    prompt = f"Summarize the topic '{topic}' from the following PDF content in 3-4 easy sentences:\n{pdf_text[:4000]}"
    summary = quiz_generator.get_topic_summary(prompt)
    return summary

def play_summary_audio(summary_text, topic):
    tts = gTTS(text=summary_text, lang='en')
    filename = f"{topic}_summary.mp3"
    tts.save(filename)
    audio_file = open(filename, "rb")
    st.audio(audio_file.read(), format="audio/mp3")
    audio_file.close()
    os.remove(filename)

# --- Caching for topic extraction ---
@st.cache_data(show_spinner="Extracting topics from PDF...")
def cached_extract_topics(text):
    return quiz_generator.extract_topics(text)
# ------------------------------------

def main():
    st.title("PDF2Prep: AI Quiz, Summary & Concept Explorer")
    st.success("Welcome to PDF2Prep!")

    # Sidebar navigation
    page = st.sidebar.radio(
        "Go to",
        ("Quiz & Summary", "Ask PDF2Prep Chatbot", "Personal Notes", "Explore Topics")
    )

    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        st.session_state.pdf_text = text
        # Reset topics and summaries if new PDF uploaded
        st.session_state.concept_topics = []
        st.session_state.concept_summaries = {}
    else:
        text = st.session_state.pdf_text

    if page == "Quiz & Summary":
        question_count = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
        difficulty = st.selectbox(
            "Select difficulty level",
            options=["easy", "medium", "hard"],
            index=1
        )
        topic = st.text_input("Enter a topic or chapter to focus the quiz (optional):")

        if uploaded_file is not None:
            # --- PDF Summary Feature ---
            if st.button("Summarize PDF"):
                with st.spinner("Summarizing PDF..."):
                    try:
                        summary = quiz_generator.summarize_pdf(text)
                        st.subheader("PDF Summary (Topic-wise, Short & Easy):")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"Error generating summary: {str(e)}")
            # --- End PDF Summary Feature ---

            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    try:
                        quiz = quiz_generator.generate_quiz(text, question_count, difficulty, topic)
                        if quiz and isinstance(quiz, list) and len(quiz) > 0:
                            st.session_state.quiz = quiz
                            st.session_state.current_question = 0
                            st.session_state.score = 0
                            st.session_state.answers = []
                            st.session_state.show_results = False
                            st.session_state.quiz_start_time = time.time()  # Start timer
                            st.session_state.quiz_end_time = None
                            st.rerun()
                        else:
                            st.error("No questions were generated. Try a different topic, a shorter PDF, or a different difficulty.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Display quiz if available and not empty
            if st.session_state.quiz and len(st.session_state.quiz) > 0:
                quiz = st.session_state.quiz
                current_q = st.session_state.current_question
                
                if not st.session_state.show_results and current_q < len(quiz):
                    question = quiz[current_q]
                    st.subheader(f"Question {current_q + 1} of {len(quiz)}")
                    st.write(question["question"])

                    # --- Live Timer Display ---
                    if st.session_state.quiz_start_time:
                        elapsed = time.time() - st.session_state.quiz_start_time
                        mins, secs = divmod(int(elapsed), 60)
                        st.info(f"⏱️ Time elapsed: {mins} minutes {secs} seconds")
                    # --------------------------

                    answer = st.radio(
                        "Choose your answer:",
                        question["options"],
                        key=f"q{current_q}"
                    )
                    
                    if st.button("Submit Answer"):
                        st.session_state.answers.append(answer)
                        if answer == next((opt for opt in question["options"] if opt.startswith(question["answer"])), ""):
                            st.session_state.score += 1
                        st.session_state.current_question += 1
                        # If last question, stop timer
                        if st.session_state.current_question >= len(quiz):
                            st.session_state.quiz_end_time = time.time()
                        st.rerun()
                
                elif current_q >= len(quiz):
                    st.success(f"Quiz completed! Score: {st.session_state.score}/{len(quiz)}")
                    # Show timer
                    if st.session_state.quiz_end_time and st.session_state.quiz_start_time:
                        elapsed = st.session_state.quiz_end_time - st.session_state.quiz_start_time
                        mins, secs = divmod(int(elapsed), 60)
                        st.info(f"⏱️ Time taken: {mins} minutes {secs} seconds")
                    st.subheader("Detailed Results")
                    for i, question in enumerate(quiz):
                        st.markdown(f"**Q{i+1}: {question['question']}**")
                        your_answer = st.session_state.answers[i] if i < len(st.session_state.answers) else "No answer"
                        correct_letter = question["answer"]
                        correct_option = next((opt for opt in question["options"] if opt.startswith(correct_letter)), "N/A")
                        st.write(f"Your answer: {your_answer}")
                        st.write(f"Correct answer: {correct_option}")
                        if your_answer == correct_option:
                            st.success("Correct!")
                        else:
                            st.error("Incorrect.")
                        st.markdown("---")

                    # --- Review Mode ---
                    if st.button("Review Quiz"):
                        st.subheader("Quiz Review with Explanations")
                        for i, question in enumerate(quiz):
                            st.markdown(f"**Q{i+1}: {question['question']}**")
                            your_answer = st.session_state.answers[i] if i < len(st.session_state.answers) else "No answer"
                            correct_letter = question["answer"]
                            correct_option = next((opt for opt in question["options"] if opt.startswith(correct_letter)), "N/A")
                            st.write(f"Your answer: {your_answer}")
                            st.write(f"Correct answer: {correct_option}")
                            with st.spinner("Generating explanation..."):
                                explanation = quiz_generator.generate_explanation(
                                    question['question'],
                                    correct_option,
                                    text
                                )
                            st.info(f"Explanation: {explanation}")
                            st.markdown("---")
                            time.sleep(0.5)

                    if st.button("Restart Quiz"):
                        st.session_state.quiz = None
                        st.session_state.current_question = 0
                        st.session_state.score = 0
                        st.session_state.answers = []
                        st.session_state.show_results = False
                        st.session_state.quiz_start_time = None
                        st.session_state.quiz_end_time = None
                        st.rerun()
            else:
                st.info("No questions were generated. Try a different topic, a shorter PDF, or a different difficulty.")

    elif page == "Ask PDF2Prep Chatbot":
        st.header("🤖 Ask PDF2Prep Chatbot")
        if not st.session_state.pdf_text:
            st.warning("Please upload a PDF file from the sidebar first.")
        else:
            st.markdown("#### Ask me anything about your PDF!")
            with st.form(key="chat_form", clear_on_submit=True):
                user_question = st.text_input(
                    "Your question",
                    placeholder="Ask me anything about the uploaded PDF...",
                    key="chat_input"
                )
                send = st.form_submit_button("Send")
            if send and user_question.strip():
                with st.spinner("Getting answer from PDF2Prep Chatbot..."):
                    answer = quiz_generator.answer_from_pdf(user_question, st.session_state.pdf_text)
                    st.session_state.chat_history.append({"question": user_question, "answer": answer})

            if st.button("Clear Chat History"):
                st.session_state.chat_history = []

            # Display chat history using Streamlit chat_message
            for chat in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(f"**You:** {chat['question']}")
                with st.chat_message("assistant"):
                    st.write(f"**PDF2Prep Chatbot:** {chat['answer']}")
                st.divider()

    elif page == "Personal Notes":
        st.header("📝 Personal Notes")
        st.info("Write and save your personal notes here. These notes are private and will remain available as long as your session is active.")
        notes = st.text_area(
            "Your Notes",
            value=st.session_state.personal_notes,
            height=250,
            key="personal_notes_area"
        )
        if st.button("Save Notes"):
            st.session_state.personal_notes = notes
            st.success("Your notes have been saved!")

    elif page == "Explore Topics":
        st.header("📚 Interactive Concept Explorer")
        if not st.session_state.pdf_text:
            st.warning("Please upload a PDF file from the sidebar first.")
        else:
            text = st.session_state.pdf_text
            # Extract topics if not already done
            if not st.session_state.concept_topics:
                with st.spinner("Extracting topics from PDF..."):
                    st.session_state.concept_topics = cached_extract_topics(text)

            topics = st.session_state.concept_topics

            if not topics:
                st.info("No topics found in the PDF. Try uploading a different PDF.")
            else:
                for topic in topics:
                    with st.expander(topic):
                        # Get summary (cache in session state)
                        if topic not in st.session_state.concept_summaries:
                            with st.spinner(f"Generating summary for {topic}..."):
                                summary = get_topic_summary(topic, text)
                                st.session_state.concept_summaries[topic] = summary
                        else:
                            summary = st.session_state.concept_summaries[topic]
                        st.write(summary)

                        # Audio explanation
                        if st.button(f"🔊 Listen to {topic} Summary", key=f"audio_{topic}"):
                            play_summary_audio(summary, topic)

                        # Related videos
                        search_url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
                        st.markdown(f"[▶️ Watch related videos on YouTube]({search_url})")

                        # Ask chatbot about this topic
                        user_topic_question = st.text_input(
                            f"Ask PDF2Prep Chatbot about '{topic}':",
                            key=f"chat_{topic}"
                        )
                        if st.button(f"Ask about {topic}", key=f"ask_{topic}"):
                            with st.spinner("Getting answer from PDF2Prep Chatbot..."):
                                answer = quiz_generator.answer_from_pdf(user_topic_question, text)
                                st.info(answer)

if __name__ == "__main__":
    main()