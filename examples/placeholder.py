import streamlit as st

title = st.empty()
page_title = st.text_input('What should the title be?')
title.title(page_title)