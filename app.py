import streamlit as st
import PyPDF2
import io
import time
from src.llama_quiz_generator import QuizGenerator

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

quiz_generator = QuizGenerator()

def main():
    st.title("PDF2Prep: AI Quiz & Summary Generator from PDF")
    st.success("Welcome to PDF2Prep!")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    question_count = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
    difficulty = st.selectbox(
        "Select difficulty level",
        options=["easy", "medium", "hard"],
        index=1
    )
    topic = st.text_input("Enter a topic or chapter to focus the quiz (optional):")

    if uploaded_file is not None:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        text = " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

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
                    st.rerun()
            
            elif current_q >= len(quiz):
                st.success(f"Quiz completed! Score: {st.session_state.score}/{len(quiz)}")
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
                    st.rerun()
        else:
            st.info("No questions were generated. Try a different topic, a shorter PDF, or a different difficulty.")

if __name__ == "__main__":
    main()