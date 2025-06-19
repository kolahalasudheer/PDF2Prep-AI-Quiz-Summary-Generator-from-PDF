# AI Quiz Generator & Summarizer

This application generates quizzes from PDF documents using AI. It now uses the Cohere API to generate high-quality questions and answers.

## Features

- Upload PDF documents
- Generate multiple-choice questions
- Interactive quiz interface
- Score tracking
- Detailed results review

## Setup

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your Cohere API key:
   - Go to [Cohere Dashboard](https://dashboard.cohere.com/api-keys) and sign in with your Cohere account
   - Click "Create API Key" and copy your key
   - Create a `.env` file in the project root directory
   - Add your key to the `.env` file:
     ```
     COHERE_API_KEY=your_actual_cohere_api_key_here
     ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the application in your web browser
2. Upload a PDF file
3. Select the number of questions you want to generate
4. Click "Generate Quiz"
5. Answer the questions
6. Review your results

## Technical Details

- Built with Streamlit for the web interface
- Uses PyPDF2 for PDF processing
- Powered by Cohere Command model
- Implements advanced prompt engineering for high-quality question generation

## Requirements

- Python 3.8+
- Internet connection for API access
- Cohere API key

## Notes

- The quality of generated questions depends on the content of the PDF
- Processing time may vary based on the size of the PDF and number of questions
- Make sure your PDF is text-based (not scanned images) for best results

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
