import os
import PyPDF2
import spacy
import streamlit as st
import pandas as pd

# Load the required spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # Download the model if it's not available
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Define a dictionary of keywords and scores
keywords = {
    'Python': 5,
    'Java': 3,
    'Machine Learning': 7,
    'Data Analysis': 4
}

# Load the spacy model
nlp = spacy.load('en_core_web_sm')

# Create the Streamlit app
def app():
    st.title('CV Keyword Rating App')

    # Create a file uploader for PDF files
    uploaded_files = st.file_uploader('Upload one or more CVs in PDF format', type='pdf', accept_multiple_files=True)

    if uploaded_files is not None:
        # Create a list to store the results
        results = []

        # Analyze each file
        for uploaded_file in uploaded_files:
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ''

            for page in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page].extract_text()

            # Analyze the text for keywords
            doc = nlp(text)
            score = 0

            for keyword, weight in keywords.items():
                count = sum(1 for token in doc if token.text.lower() == keyword.lower())
                score += count * weight

            # Add the results to the list
            filename = uploaded_file.name
            results.append({'Filename': filename, 'Score': score, **keywords})

        # Display the results in a table
        df = pd.DataFrame(results)
        st.write(df)

if __name__ == '__main__':
    app()
