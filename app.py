import os
import PyPDF2
import streamlit as st
import pandas as pd
from collections import defaultdict
import re

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# Define a regex pattern to match emails
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def app():
    st.title('CV Keyword Rating App')
    st.text('Add your Categories, Keywords entire each Category & Score')
    # Get user input for categories, keywords, and scores
    categories = {}
    num_categories = st.number_input('Number of categories', min_value=1, max_value=10, value=5, key='categories')
    for i in range(num_categories):
        category_name = st.text_input(f'Category {i+1} name', key=f'category_name_{i}')
        num_keywords = st.number_input(f'Number of keywords for {category_name}', min_value=1, max_value=20, value=3, key=f'num_keywords_{i}')
        keywords = {}
        for j in range(num_keywords):
            keyword_name = st.text_input(f'Keyword {j+1} for {category_name}', key=f'keyword_name_{i}_{j}')
            keyword_score = st.number_input(f'Score for {keyword_name}', min_value=1, max_value=10, value=3, key=f'keyword_score_{i}_{j}')
            keywords[keyword_name.lower()] = keyword_score
        categories[category_name.lower()] = keywords

    # Create a file uploader for PDF files
    uploaded_files = st.file_uploader('Upload one or more CVs in PDF format', type='pdf', accept_multiple_files=True, key='uploaded_files')

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

            # Remove newlines, extra spaces and tabs from text
            text = re.sub(r'\n', ' ', text)
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\t', '', text)

            # Remove email addresses from text
            text = re.sub(email_regex, '', text)

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
