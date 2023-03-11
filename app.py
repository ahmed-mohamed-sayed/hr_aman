import os
import PyPDF2
import streamlit as st
import pandas as pd
from collections import defaultdict

# Define a dictionary of categories and their corresponding keywords and scores
categories = {
    'optimization': {
        'tuning': 3,
        'performance': 2,
        'query performance': 1,
        'tuning advisor': 1
    },
    'tuning': {
        'tuning': 4,
        'performance': 2,
        'query performance': 2,
        'tuning advisor': 1
    },
    'performance': {
        'tuning': 2,
        'performance': 4,
        'query performance': 2,
        'tuning advisor': 1
    },
    'query performance': {
        'tuning': 1,
        'performance': 2,
        'query performance': 3,
        'tuning advisor': 2
    },
    'tuning advisor': {
        'tuning': 1,
        'performance': 1,
        'query performance': 2,
        'tuning advisor': 3
    }
}

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
            category_scores = defaultdict(int)
            total_score = 0

            # Check for keywords in the text
            for category, keywords in categories.items():
                category_score = 0
                for keyword, score in keywords.items():
                    if keyword in text.lower():
                        category_score += score
                        total_score += score
                category_scores[category] = category_score

            # Calculate full score and score percentage
            full_score = sum(categories[c].get(k, 0) for c in categories for k in categories[c])
            score_pct = total_score / full_score if full_score > 0 else 0

            # Add the results to the list
            filename = uploaded_file.name
            result = {'Filename': filename,'Full Score': full_score, 'CV Score': total_score,  'Score PCT%': (str(round(score_pct*100))+'%')}
            result.update(category_scores)
            results.append(result)

        # Display the results in a table
        df = pd.DataFrame(results)
        st.write(df)

if __name__ == '__main__':
    app()
