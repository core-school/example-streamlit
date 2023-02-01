import streamlit as st
st.set_page_config(page_title="Column Explorer", page_icon="🤠", layout="wide")

st.title("Divinding in columns and color picking")

# Default colors for initial value
colors = ["#FFC0CB", "#2E8B57", "#BA55D3", "#4169E1", "#F4A460", "#696969", "#F5F5DC", "#FF1493", "#FFFF00", "#00FA9A"]

# n columns
n = st.slider("How many columns?", 1, 10, 5, 1)
columns = st.beta_columns(n)
div_colors = {}
for i in range(1,n+1):
    with columns[i-1]:
        col = st.color_picker("",colors[i-1],key=f"column {i}")
        st.markdown(f'<div class="div-{i} column"> Hello </div>'
                                , unsafe_allow_html=True)
        div_colors[i] = col

st.write("---")

# 2 columns proportionally divided
prop = st.slider("Divide the columns", 1, 99, 50, 1)
prop_columns = st.beta_columns((prop,100-prop))
with prop_columns[0]:
    col = st.color_picker("","#F5F5DC",key=f"left")
    st.markdown('<div class="div-left column"> Left </div>', unsafe_allow_html=True)
    div_colors["left"] = col

with prop_columns[1]:
    col = st.color_picker("","#696969",key=f"right")
    st.markdown('<div class="div-right column"> Right </div>', unsafe_allow_html=True)
    div_colors["right"] = col

# Creating and writing the style tag for the colors on the columns above
colors = "\n".join([f".div-{i} {{background-color: {c}}}" for i,c in div_colors.items()])
css = f"""<style>
    .column {{text-align: center; color: black}}
    {colors}
    </style>"""
st.markdown(css, unsafe_allow_html=True)