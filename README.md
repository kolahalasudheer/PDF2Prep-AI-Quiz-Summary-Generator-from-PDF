# PDF2Prep

**PDF2Prep** is an AI-powered Streamlit app that helps you learn from any PDF by generating quizzes, summaries, topic explorers, and more!

---

## 🚀 Features

- **Quiz & Summary:**  
  Generate multiple-choice quizzes and concise summaries from any PDF.
- **Ask PDF2Prep Chatbot:**  
  Ask questions about your PDF and get instant, context-aware answers.
- **Personal Notes:**  
  Write and save your own notes while studying.
- **Explore Topics (Interactive Concept Explorer):**  
  - Automatically extracts main topics/chapters from your PDF.
  - For each topic, see a summary, listen to an audio explanation, get related YouTube videos, and ask the chatbot about that topic.

---

## 🖥️ How to Run

1. **Clone this repository** and navigate to the project folder.

2. **Install dependencies:**
    

https://github.com/user-attachments/assets/52667c7f-8695-419e-914c-09ed89723b95

```sh
    pip install -r requirements.txt
    ```

3. **Set up your Cohere API key:**
    - Create a `.env` file in the root directory.
    - Add:
      ```
      COHERE_API_KEY=your_cohere_api_key_here
      ```

4. **Run the app:**
    ```sh
    streamlit run app.py
    ```

---

## 📄 Usage

1. **Upload a PDF** using the sidebar.
2. **Navigate** using the sidebar menu:
    - **Quiz & Summary:** Generate and take quizzes, or get a summary.
    - **Ask PDF2Prep Chatbot:** Ask any question about your PDF.
    - **Personal Notes:** Write and save your own notes.
    - **Explore Topics:** Click to expand topics, read/listen to summaries, watch related videos, and ask topic-specific questions.

---

## 🛠️ Requirements

- Python 3.8+
- [Streamlit](https://streamlit.io/)
- [PyPDF2](https://pypdf2.readthedocs.io/)
- [gTTS](https://pypi.org/project/gTTS/)
- [cohere](https://docs.cohere.com/docs/quickstart)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install all dependencies with:
```sh
pip install streamlit PyPDF2 gtts cohere python-dotenv
```

---

## 📢 Notes

- The **Explore Topics** feature works best with text-based (not scanned/image) PDFs.
- The app uses Cohere’s LLM for all AI features. Make sure your API key is valid and you have quota.
- Audio summaries require an internet connection (for gTTS).

---

## 🤝 Contributing

Pull requests and suggestions are welcome!

---

## 📃 License

MIT License

---

**Enjoy learning with PDF2Prep!**

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables
└── src/
    ├── pdf_processor.py  # PDF text extraction
    ├── quiz_generator.py # AI quiz generation
    └── utils.py         # Utility functions
``` 

