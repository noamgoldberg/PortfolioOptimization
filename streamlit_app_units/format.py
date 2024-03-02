import streamlit as st


def format_app_markdown():
    st.markdown(
        '''
        <style>
        [data-testid="stMarkdownContainer"] ul{
            padding-left:40px;
        }
        </style>
        ''', 
        unsafe_allow_html=True
    )