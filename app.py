import os
import PyPDF2
import streamlit as st
import pandas as pd
from collections import defaultdict
import re
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_option_menu import option_menu



# Set page title and favicon
st.set_page_config(page_title="CV Ratings", page_icon="N5ZUyMw5.ico" , layout='wide')

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

st.markdown("""
        <style>
        .logout-button {
            width: 200%;
        }
        </style>
        """, unsafe_allow_html=True)


with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')


if st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
elif st.session_state["authentication_status"]:
    
    

    def app():
        # Set Navigation Menu

        with st.sidebar:
            
            st.write(f'<h1 style="font-size: 26px;">Welcome {st.session_state["name"]}</h1>', unsafe_allow_html=True)
            
            selected = option_menu(
                menu_title = 'Departments',
                options = ['DBA','Analytics', 'Finance' ],
                icons=['house','bar-chart','coin'],
                menu_icon='cast',
                default_index = 0,
                styles={
                        "container": {"padding": "0!important", "background-color": "#fafafa"},
                        "icon": {"color": "orange", "font-size": "15px"},
                        "nav-link": {
                            "font-size": "15px",
                            "text-align": "left",
                            "margin": "0px",
                            "--hover-color": "#f0f0f0",
                        },
                        "nav-link-selected": {"background-color": '#C00000'},
                    },
                                     
        )
            authenticator.logout('Logout', 'sidebar')
        if selected == 'DBA':
            st.markdown("<h2 style='text-align: center; font-weight:bold; color: #354968;'> Databse Department</h2> " ,unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center; font-weight:bold; color: #C00000;'> 'Categories are predefined. Please add your keywords & score entire each category' </h5> " ,unsafe_allow_html=True)
            #bold line separator:
            st.markdown("""<hr style="height:2x;border:none;color:#C00000;background-color:#C00000;" /> """, unsafe_allow_html=True)
            # Define a regex pattern to match emails
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # Define the predefined categories
            CATEGORIES = {
                'Optimization': {},
                'Performance': {},
                'Tuning': {}
            }

            # Get user input for the keywords and scores
            for category_name in CATEGORIES:
                num_keywords = st.number_input(f'Number of keywords for {category_name}', min_value=1, max_value=20, value=1, key=f'num_keywords_{category_name}')
                keywords = {}
                for j in range(num_keywords):
                    keyword_name = st.text_input(f'Keyword {j+1} for {category_name}', key=f'keyword_name_{category_name}_{j}')
                    keyword_score = st.number_input(f'Score for {keyword_name}', min_value=1, max_value=10, value=3, key=f'keyword_score_{category_name}_{j}')
                    keywords[keyword_name.lower()] = keyword_score
                CATEGORIES[category_name] = keywords

            # Get user input for the scores
            # scores = {}
            # for category_name, keywords in CATEGORIES.items():
            #     for keyword_name, default_score in keywords.items():
            #         score = st.number_input(f'Score for "{keyword_name}" in "{category_name}"', min_value=1, max_value=10, value=default_score)
            #         scores[f'{category_name}_{keyword_name}'] = score


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
                    # Extracting Work Experience from the text
                    work_experience = ''
                    work_experience_regex = r'(?i)work\sexperience'
                    match = re.search(work_experience_regex, text)
                    if match:
                        start_index = match.end()
                        # Check if there is a line break after the "work experience" text
                        if text[start_index:start_index+1] == '\n':
                            start_index += 1
                        # Find the end of the work experience section (look for the next section header)
                        end_index = len(text)
                        for category in CATEGORIES.keys():
                            category_regex = r'(?i)' + category
                            match = re.search(category_regex, text[start_index:])
                            if match:
                                end_index = min(end_index, match.start() + start_index)
                        # Extract the work experience section
                        work_experience = text[start_index:end_index]
                        # Remove newlines, extra spaces and tabs from work experience text
                        work_experience = re.sub(r'\n', ' ', work_experience)
                        work_experience = re.sub(r' +', ' ', work_experience)
                        work_experience = re.sub(r'\t', '', work_experience)
                    # Analyze the text for keywords
                    category_scores = defaultdict(int)
                    total_score = 0

                    # Check for keywords in the text
                    for category, keywords in CATEGORIES.items():
                        category_score = 0
                        for keyword, score in keywords.items():
                            if keyword in text.lower():
                                category_score += score
                                total_score += score
                        category_scores[category] = category_score

                    # Calculate full score and score percentage
                    full_score = sum(CATEGORIES[c].get(k, 0) for c in CATEGORIES for k in CATEGORIES[c])
                    score_pct = total_score / full_score if full_score > 0 else 0

                    # Add the results to the list
                    filename = uploaded_file.name
                    result = {'Filename': filename,'Full Score': full_score, 'CV Score': total_score,  'Score PCT%': (str(round(score_pct*100))+'%')}
                    result.update(category_scores)
                    results.append(result)

                # Display the results in a table
                df = pd.DataFrame(results)
                st.write(df)
        if selected == 'Analytics':
            st.markdown("<h2 style='text-align: center; font-weight:bold; color: #354968;'> Analytics Department</h2> " ,unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center; font-weight:bold; color: #C00000;'> 'Categories are predefined. Please add your keywords & score entire each category' </h5> " ,unsafe_allow_html=True)
            #bold line separator:
            st.markdown("""<hr style="height:2x;border:none;color:#C00000;background-color:#C00000;" /> """, unsafe_allow_html=True)
            # Define a regex pattern to match emails
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # Define the predefined categories
            CATEGORIES = {
                'Visualization': {},
                'Manipulation': {},
                'Regression': {}
            }

            # Get user input for the keywords and scores
            for category_name in CATEGORIES:
                num_keywords = st.number_input(f'Number of keywords for {category_name}', min_value=1, max_value=20, value=1, key=f'num_keywords_{category_name}')
                keywords = {}
                for j in range(num_keywords):
                    keyword_name = st.text_input(f'Keyword {j+1} for {category_name}', key=f'keyword_name_{category_name}_{j}')
                    keyword_score = st.number_input(f'Score for {keyword_name}', min_value=1, max_value=10, value=3, key=f'keyword_score_{category_name}_{j}')
                    keywords[keyword_name.lower()] = keyword_score
                CATEGORIES[category_name] = keywords

            # Get user input for the scores
            # scores = {}
            # for category_name, keywords in CATEGORIES.items():
            #     for keyword_name, default_score in keywords.items():
            #         score = st.number_input(f'Score for "{keyword_name}" in "{category_name}"', min_value=1, max_value=10, value=default_score)
            #         scores[f'{category_name}_{keyword_name}'] = score


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
                    # Extracting Work Experience from the text
                    work_experience = ''
                    work_experience_regex = r'(?i)work\sexperience'
                    match = re.search(work_experience_regex, text)
                    if match:
                        start_index = match.end()
                        # Check if there is a line break after the "work experience" text
                        if text[start_index:start_index+1] == '\n':
                            start_index += 1
                        # Find the end of the work experience section (look for the next section header)
                        end_index = len(text)
                        for category in CATEGORIES.keys():
                            category_regex = r'(?i)' + category
                            match = re.search(category_regex, text[start_index:])
                            if match:
                                end_index = min(end_index, match.start() + start_index)
                        # Extract the work experience section
                        work_experience = text[start_index:end_index]
                        # Remove newlines, extra spaces and tabs from work experience text
                        work_experience = re.sub(r'\n', ' ', work_experience)
                        work_experience = re.sub(r' +', ' ', work_experience)
                        work_experience = re.sub(r'\t', '', work_experience)
                    # Analyze the text for keywords
                    category_scores = defaultdict(int)
                    total_score = 0

                    # Check for keywords in the text
                    for category, keywords in CATEGORIES.items():
                        category_score = 0
                        for keyword, score in keywords.items():
                            if keyword in text.lower():
                                category_score += score
                                total_score += score
                        category_scores[category] = category_score

                    # Calculate full score and score percentage
                    full_score = sum(CATEGORIES[c].get(k, 0) for c in CATEGORIES for k in CATEGORIES[c])
                    score_pct = total_score / full_score if full_score > 0 else 0

                    # Add the results to the list
                    filename = uploaded_file.name
                    result = {'Filename': filename,'Full Score': full_score, 'CV Score': total_score,  'Score PCT%': (str(round(score_pct*100))+'%')}
                    result.update(category_scores)
                    results.append(result)

                # Display the results in a table
                df = pd.DataFrame(results)
                st.write(df)
        if selected == 'Finance':
            st.markdown("<h2 style='text-align: center; font-weight:bold; color: #354968;'> Finance  Department</h2> " ,unsafe_allow_html=True)
            st.markdown("<h5 style='text-align: center; font-weight:bold; color: #C00000;'> 'Categories are predefined. Please add your keywords & score entire each category' </h5> " ,unsafe_allow_html=True)
            #bold line separator:
            st.markdown("""<hr style="height:2x;border:none;color:#C00000;background-color:#C00000;" /> """, unsafe_allow_html=True)
            # Define a regex pattern to match emails
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        # Define the predefined categories
            CATEGORIES = {
                'Balance Sheet': {},
                'A/R': {},
                'A/P': {}
            }

            # Get user input for the keywords and scores
            for category_name in CATEGORIES:
                num_keywords = st.number_input(f'Number of keywords for {category_name}', min_value=1, max_value=20, value=1, key=f'num_keywords_{category_name}')
                keywords = {}
                for j in range(num_keywords):
                    keyword_name = st.text_input(f'Keyword {j+1} for {category_name}', key=f'keyword_name_{category_name}_{j}')
                    keyword_score = st.number_input(f'Score for {keyword_name}', min_value=1, max_value=10, value=3, key=f'keyword_score_{category_name}_{j}')
                    keywords[keyword_name.lower()] = keyword_score
                CATEGORIES[category_name] = keywords

            # Get user input for the scores
            # scores = {}
            # for category_name, keywords in CATEGORIES.items():
            #     for keyword_name, default_score in keywords.items():
            #         score = st.number_input(f'Score for "{keyword_name}" in "{category_name}"', min_value=1, max_value=10, value=default_score)
            #         scores[f'{category_name}_{keyword_name}'] = score


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
                    # Extracting Work Experience from the text
                    work_experience = ''
                    work_experience_regex = r'(?i)work\sexperience'
                    match = re.search(work_experience_regex, text)
                    if match:
                        start_index = match.end()
                        # Check if there is a line break after the "work experience" text
                        if text[start_index:start_index+1] == '\n':
                            start_index += 1
                        # Find the end of the work experience section (look for the next section header)
                        end_index = len(text)
                        for category in CATEGORIES.keys():
                            category_regex = r'(?i)' + category
                            match = re.search(category_regex, text[start_index:])
                            if match:
                                end_index = min(end_index, match.start() + start_index)
                        # Extract the work experience section
                        work_experience = text[start_index:end_index]
                        # Remove newlines, extra spaces and tabs from work experience text
                        work_experience = re.sub(r'\n', ' ', work_experience)
                        work_experience = re.sub(r' +', ' ', work_experience)
                        work_experience = re.sub(r'\t', '', work_experience)
                    # Analyze the text for keywords
                    category_scores = defaultdict(int)
                    total_score = 0

                    # Check for keywords in the text
                    for category, keywords in CATEGORIES.items():
                        category_score = 0
                        for keyword, score in keywords.items():
                            if keyword in text.lower():
                                category_score += score
                                total_score += score
                        category_scores[category] = category_score

                    # Calculate full score and score percentage
                    full_score = sum(CATEGORIES[c].get(k, 0) for c in CATEGORIES for k in CATEGORIES[c])
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
    