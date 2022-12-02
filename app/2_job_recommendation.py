"""
# My first app
Here's our first attempt at using data to create a table:
"""

import streamlit as st
import pandas as pd
import PyPDF2
import os
from PIL import Image
import spacy
import re
import string
from nltk.corpus import stopwords
from wordcloud import WordCloud
from wordcloud import WordCloud, STOPWORDS

st.set_page_config(
    page_title="Discover Your Job ",
    page_icon="👋",
    layout="wide"
)

st.write("# Welcome to KG Job Helper System!")

# add elements in the side bar
# Using "with" notation
with st.sidebar:
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
      st.write("")

    with col2:
      image = Image.open(r'./static/jobs.jpg')
      st.image(image, caption='Job Helper System',use_column_width='auto')

    with col3:
      st.write("")

