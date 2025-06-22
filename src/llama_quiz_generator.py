import os
import ast
import json
import random
import re
from dotenv import load_dotenv
import cohere
import streamlit as st

load_dotenv()

class QuizGenerator:
    def __init__(self):
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            raise ValueError("Cohere API key not found in environment variables")
        self.co = cohere.Client(api_key)

    def chunk_text(self, text, max_length=3000):
        """Splits text into chunks for processing."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def generate_quiz(self, text, question_count, difficulty="medium", topic=""):
        """Generates a quiz from the PDF text."""
        topic_instruction = f" Focus ONLY on the topic/chapter: '{topic}'." if topic else ""
        chunks = self.chunk_text(text)
        questions_per_chunk = max(1, question_count // len(chunks))
        all_questions = []
        remaining_questions = question_count
        for chunk in chunks:
            if remaining_questions <= 0:
                break
            chunk_questions = min(questions_per_chunk, remaining_questions)
            prompt = f"""
            Generate {chunk_questions} multiple choice questions from this text.
            The questions should be of {difficulty} difficulty.{topic_instruction}
            For each question, provide:
            1. The question text
            2. Four options labeled A, B, C, D
            3. The correct answer letter

            Format the output as a list of dictionaries:
            [
                {{"question": "What is...", 
                  "options": ["A) First", "B) Second", "C) Third", "D) Fourth"],
                  "answer": "A"}}
            ]

            Text: {chunk}
            """
            try:
                response = self.co.generate(
                    model='command',
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=0.7,
                    k=0,
                    stop_sequences=[],
                    return_likelihoods='NONE'
                )
                generated_text = response.generations[0].text
                try:
                    quiz_text = generated_text.replace("```json", "").replace("```", "").strip()
                    chunk_data = json.loads(quiz_text)
                    if isinstance(chunk_data, list):
                        all_questions.extend(chunk_data)
                        remaining_questions -= len(chunk_data)
                except json.JSONDecodeError:
                    continue
            except Exception:
                continue

        # Shuffle options for each question and update the answer letter accordingly
        for question in all_questions:
            options = question["options"]
            correct_letter = question["answer"]
            correct_option = next((opt for opt in options if opt.startswith(correct_letter)), None)
            random.shuffle(options)
            for idx, opt in enumerate(options):
                if opt == correct_option:
                    question["answer"] = ["A", "B", "C", "D"][idx]
            question["options"] = options

        return all_questions if all_questions else []

    def generate_explanation(self, question, correct_option, text):
        """Generates an explanation for a quiz question."""
        prompt = f"""
        Explain why the correct answer to the following multiple choice question is {correct_option}.

        Question: {question}
        Correct Option: {correct_option}
        Context: {text[:1000]}
        """
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=150,
                temperature=0.5,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            return response.generations[0].text.strip()
        except Exception:
            return "Explanation not available."

    def summarize_pdf(self, text):
        """Summarizes the PDF content in a topic-wise manner."""
        prompt = """
        Summarize the following PDF content in a topic-wise manner. For each topic or chapter, provide a short, crisp, and easy-to-understand explanation (2-3 sentences per topic) so that a beginner can quickly grasp the main ideas.

        PDF Content:
        """ + text[:4000]  # Limit to avoid token overflow

        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=400,
                temperature=0.5,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            return response.generations[0].text.strip()
        except Exception:
            return "Summary not available."

    def answer_from_pdf(self, question, pdf_text):
        """Answers a question based on the PDF content."""
        prompt = f"""
        You are a helpful assistant. Answer the following question based only on the provided PDF content. 
        If the answer is not present in the PDF, say "Sorry, I couldn't find the answer in the PDF."

        PDF Content:
        {pdf_text[:4000]}

        Question: {question}
        Answer:
        """
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=200,
                temperature=0.3,
                k=0,
                stop_sequences=[],
                return_likelihoods='NONE'
            )
            return response.generations[0].text.strip()
        except Exception:
            return "Sorry, I couldn't process your question right now."

    def extract_topics(self, pdf_text):
        """
        Extracts ONLY the MAIN topics or chapters from the PDF content.
        Returns a clean Python list of strings.
        Handles LLM quirks robustly.
        """
        prompt = (
            "List ONLY the MAIN topics or chapters (not subtopics or details) from the following PDF content. "
            "Return ONLY a Python list of strings, with each main topic or chapter as a separate string. "
            "Do NOT add any explanation or extra text. Example: ['Chapter 1: Introduction', 'Chapter 2: Data Structures', 'Chapter 3: Algorithms']\n\n"
            f"PDF Content:\n{pdf_text[:4000]}"
        )
        response = self.co.generate(
            model='command',
            prompt=prompt,
            max_tokens=300,
            temperature=0.3,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        raw = response.generations[0].text.strip()
        st.write("LLM raw output:", raw)  # Debug line

        # Use regex to extract the first list-like string
        match = re.search(r"\[[^\[\]]+\]", raw, re.DOTALL)
        if match:
            list_str = match.group(0)
            try:
                topics = ast.literal_eval(list_str)
                if isinstance(topics, list):
                    topics = [t.strip() for t in topics if t.strip()]
                    topics = list(dict.fromkeys(topics))  # Remove duplicates, preserve order
                    st.info(f"Extracted topics: {topics}")
                    return topics
            except Exception as e:
                st.error(f"Topic extraction error: {e}")

        # Fallback: try to split lines if not a list
        topics = []
        for line in raw.splitlines():
            line = line.strip("-* \n")
            if line and not line.startswith("Let me know"):
                topics.append(line)
        # Handle case where first element is a stringified list
        if topics and isinstance(topics, list):
            first = topics[0]
            if isinstance(first, str) and first.strip().startswith("[") and first.strip().endswith("]"):
                try:
                    inner_topics = ast.literal_eval(first)
                    if isinstance(inner_topics, list):
                        inner_topics = [t.strip() for t in inner_topics if t.strip()]
                        inner_topics = list(dict.fromkeys(inner_topics))
                        st.info(f"Recovered topics from string: {inner_topics}")
                        return inner_topics
                except Exception as e:
                    st.error(f"Nested topic extraction error: {e}")
            # Otherwise, filter out non-topic lines
            topics = [t for t in topics if "[" not in t and "Let me know" not in t]
            topics = [t.strip() for t in topics if t.strip()]
            topics = list(dict.fromkeys(topics))
            st.info(f"Cleaned fallback topics: {topics}")
            return topics

        st.info("No topics found.")
        return []

    def get_topic_summary(self, prompt):
        """Gets a summary for a specific topic."""
        response = self.co.generate(
            model='command',
            prompt=prompt,
            max_tokens=150,
            temperature=0.5,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        return response.generations[0].text.strip()