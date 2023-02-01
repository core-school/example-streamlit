import streamlit as st
from random import choice
st.set_page_config(page_title="Magic 8 Ball", page_icon="🎱", layout="wide")

st.title("Magic 8 Ball")

user_name = st.text_input('Tell me your name...')
button_press = st.button("Try your luck")

phrases = ["As I see it, yes.",
           "Ask again later.",
           "Better not tell you now.",
           "Cannot predict now.",
           "Concentrate and ask again.",
           "Don’t count on it.",
           "It is certain.",
           "It is decidedly so.",
           "Most likely.",
           "My reply is no.",
           "My sources say no.",
           "Outlook not so good.",
           "Outlook good.",
           "Reply hazy, try again.",
           "Signs point to yes.",
           "Very doubtful.",
           "Without a doubt.",
           "Yes.",
           "Yes – definitely.",
           "You may rely on it"]

if button_press:
    st.header(f"Let's see, {user_name}...")
    st.title(choice(phrases))