import os
from dotenv import load_dotenv
import cohere
import json
import random

load_dotenv()

class QuizGenerator:
    def __init__(self):
        api_key = os.getenv('COHERE_API_KEY')
        if not api_key:
            raise ValueError("Cohere API key not found in environment variables")
        self.co = cohere.Client(api_key)

    def chunk_text(self, text, max_length=3000):
        """Split text into chunks of max_length characters"""
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
            except Exception as e:
                continue

        # Shuffle options for each question and update the answer letter accordingly
        for question in all_questions:
            options = question["options"]
            correct_letter = question["answer"]
            # Find the correct option text
            correct_option = next((opt for opt in options if opt.startswith(correct_letter)), None)
            # Shuffle options
            random.shuffle(options)
            # Update the answer letter based on new position
            for idx, opt in enumerate(options):
                if opt == correct_option:
                    question["answer"] = ["A", "B", "C", "D"][idx]
            question["options"] = options

        return all_questions if all_questions else []

    def generate_explanation(self, question, correct_option, text):
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
        except Exception as e:
            return "Explanation not available."

    def summarize_pdf(self, text):
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
        except Exception as e:
            return "Summary not available."