import streamlit as st
import pandas as pd
from math import ceil
import plotly.express as px
import json
import base64

# set_page_config must be the first streamlit command
st.set_page_config(page_title="X-Files", page_icon="🛸", layout='wide',initial_sidebar_state="collapsed")

# This will disable the options menu and the footer
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

# This removes bottom and top paddings
st.markdown(
        """
<style>
    .reportview-container .main .block-container {
        padding-top: 0px;
        padding-bottom: 0px;
    }
</style>
""",
        unsafe_allow_html=True,
    )

# Making a Header with image
# We use columns to center the image
header = st.beta_columns((1,6,1))
with header[1]:
    st.image("img/xfiles_banner.jpeg")

# A title for our app
# The title can be centered with Markdown/HTML
title = """
<h1 style="text-align:center">
X-Files: UFO Sightings reported by the NUFORC
</h1>
"""
st.markdown(title, unsafe_allow_html=True)

# Body
# We will have two main objects on our app
body = st.beta_columns((2,2))
with body[0]:
    # Header
    st.header("Map")
    # Dropbox
    map_type = st.selectbox('', ["Global distribution","By country","By state (US only)"])
    # Placeholder
    st.empty()

with body[1]:
    st.header("Over the years")
    years_plot = st.selectbox('', ["Number of sightings","Duration of sights (avg)"])
    st.empty()

# Load Data
# We load the data now because it will be necessary for the following selectors
df = pd.read_csv("data/clean.csv")
df["duration (seconds)"] = df["duration (seconds)"].astype(float)

# Selection Slider
# We calculate the limits
min_year, max_year = int(df.year.min()), int(df.year.max())
# We set name, min, max, (starting positions), step
date_range = st.slider("Date Range", min_year, max_year,(min_year, max_year), 1)

# Multiple select
# Dropboxes that allow for multiple selection
selector = st.beta_columns((2,2))
with selector[0]:
    shapes = st.multiselect('UFO shape', sorted(df["shape"].unique()))

with selector[1]:
    # If the map type was selected, since it comes previously on the code, we limit this selector
    if map_type == "By state (US only)":
        country_selec = st.multiselect('Countries', ["United States of America"])
    # Otherwise we will set all available countries as options        
    else:
        # We use the Alpha-3 code to Name conversor for a better UI
        with open('data/code_name.json','r') as data:
                code_name = json.load(data)
        # Also sorting it to have it alphabetically
        all_countries = sorted([code_name[x] for x in df["country"].unique()])
        country_selec = st.multiselect('Countries', all_countries)

# This function will come handy soon
def draw_flags(countries):
    n = len(countries)
    # We divide the countries in rows of eight
    for i in range(ceil(n/8)):
        flags = st.beta_columns(8)
        # And put the flag image of 8 countries in each row
        for j in range(8):
            with flags[j]:
                try:
                    st.image(f"data/flags/{countries[i*8+j]}.png")
                except: pass

######################################################################################
# All the interactive part of the main body of the app ended here.                   #
# The following will use the values adquired from the widgets to filter the dataset  #
# and put the correct graphics on the previously defined placeholders.               #
######################################################################################

# Filter Data
## Year
## We use our first parameter to get only the entries within the specified range
df = df[df.year.between(*date_range)]

## Shape
## The multiple selector box will give us values for the shapes
## In case no value was selected (When first opening the app)
## then all shapes will be included
if not shapes: 
    shapes = df["shape"].unique()
df = df[df["shape"].isin(shapes)]

## Country
## and the same for countries.
if not country_selec: 
    selected_countries = df["country"].unique()
else:
    # Here we do the reverse to convert all of the country names back into Alpha-3 ISO codes.
    with open('data/name_code.json','r') as data:
        name_code = json.load(data)
        selected_countries = [name_code[x] for x in country_selec]
    # And in case there are any countries selected, we call on the draw_flags function 
    # just for a little extra swag
    draw_flags(selected_countries)
df = df[df["country"].isin(selected_countries)]

# Since all the filters have been properly applied (remember that the order is important)
# We now can create the objects to fill in the previously set placeholders.

# Populate the body
with body[0]:
    # Plotly Map
    # Streamlit has a lot of it's own plotting methods, but we will be using plotly for a little extra control

    # We calculate the approximate center of all the points to set the initial position of our map
    c_lat = (df["latitude"].max()+df["latitude"].min())/2
    c_lon = (df["longitude"].max()+df["longitude"].min())/2

    # Since we have defined 3 posibilities of maps on the dropbox, we will have three different
    # cases we will have to code. These should ideally have been modulated into other files,
    # but we've decised to keep it into a single file to simplify for this workshop. 

    # The first map is a simple scatter over the world
    if map_type == "Global distribution":
        # We create a map with the points of our dataframe
        my_map = px.scatter_mapbox(df, lat="latitude", lon="longitude", hover_name="city",
                            zoom=1, center={"lat":c_lat,"lon":c_lon})
        # We use open-street-map because it needs no token
        my_map.update_layout(mapbox_style="open-street-map")
        # This sets the padding for the map within it's space
        my_map.update_layout(margin={"r":10,"t":0,"l":0,"b":0})

    # The second option is a choropleth map, therefore we will need the geojson file with the 
    # polygons that draw the borders of the countries
    if map_type == "By country":
        with open('data/countries.geojson','r') as data:
            countries = json.load(data)
        # We also group the data by country so we can get a count of entries for each
        df_choro = df.groupby("country").agg(count=("country","count")).reset_index()
        my_map = px.choropleth_mapbox(df_choro, geojson=countries, locations='country', color='count',
                                color_continuous_scale="oranges",
                                range_color=(0, 100),
                                mapbox_style="carto-positron",
                                zoom=1, center = {"lat": c_lat, "lon": c_lon},
                                opacity=0.7,
                                labels={'count':'#'}
                                )
        my_map.update_layout(margin={"r":20,"t":0,"l":0,"b":0})

    # The third option is the same as the previous, but we use a geojson of the US states and territories
    # instead of the countries.
    if map_type == "By state (US only)":
        with open('data/states.geojson','r') as data:
            states = json.load(data)
        df = df[df["country"] == "USA"]
        df_choro = df.groupby("state").agg(count=("state","count")).reset_index()
        my_map = px.choropleth_mapbox(df_choro, geojson=states, locations='state', color='count',
                                color_continuous_scale="oranges",
                                range_color=(200, 4000),
                                mapbox_style="carto-positron",
                                zoom=3, center = {"lat": 38, "lon": -97},
                                opacity=0.7,
                                labels={'count':'#'}
                                )
        my_map.update_layout(margin={"r":20,"t":0,"l":0,"b":0})

    # After creating the map with one of the cases above, we write it to the correct spot
    # st.<widget> will write to the space set on the `with` clause, or at the bottom if there is
    # no such clause
    st.plotly_chart(my_map)

with body[1]:
    # Plotly line plot
    # We use the same logic with the second part of the body, but with two different line plots instead
    # of maps.
    if years_plot == "Number of sightings":
        data = df.groupby("year").agg(count=("datetime","count"))
        plot = px.line(data, y="count", labels={"year":"Year", "count":"# Reported encounters"})

    if years_plot == "Duration of sights (avg)":
        data = df.groupby("year").agg(length=("duration (seconds)","mean"))
        plot = px.line(data, y="length", labels={"year":"Year", "length":"Average duration of encounter (seconds)"})
    
    # In both these cases we use `plotly_chart` because we are using Plotly objects, but
    # any other widget can substitute the placeholder with a new value.
    st.plotly_chart(plot)

####################################################################################
# To here, we already have a pretty cool web app, built entirely with python code  #
# and a little logic (the hardest part in using streamlit). You can imagine that   # 
# the possibilities are already awesome with this, and the interaction with the    #
# user is only limited by your creativity. But we will take it a little step       #
# to showcase another cool streamlit feature.                                      #
####################################################################################

# With the magic of a html tag and the base 64 encoder, we will use this function to generate a
# link that containd the data for a given pandas dataframe.
def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a download="data.csv" href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

# Sidebar
# The sidebar is pretty much another page, except that it is a little smaller and can be hidden.
# The way to code it is exactly the same as anything else we've seen above. The only difference
# is that we will use `st.sidebar.<widget>` instead of `st.<widget>`. All the methods and arguments
# are the same in both cases.

# A header for the sidebar
st.sidebar.header("Case Reports")

# We make a copy of the data because I chose to treat the selections on the sidebar just for the sidebar,
# but the choices on the main body will affect both.
# This is a ~choice~ of UI. It could all affect the same data or be two completely different datasets
# Use your creativity to make the best use of the tools available.
cases = df.copy()
# On the sidebar, I've decided to put in a dropbox for the city and the case number so we can take 
# a closer look on the sighting reports.
case_city = st.sidebar.selectbox('City', ["All", *sorted(df["city"].unique())])
if case_city != "All":
    cases = df[df["city"] == case_city]
case_number = st.sidebar.selectbox('Case no.', ["All", *sorted(cases.index)])
if case_number != "All":
    cases = df.loc[case_number,:]

# Given the selection, we display a simplified dataframe. It is on a very limited space and we will use
# it as more of a searching tool than anything else.
# We limit the number of rows because this dataset is huge and pushes on streamlits limitations.
st.sidebar.dataframe(cases[['datetime', 'city', 'state', 'country', 'shape',
            'duration (hours/min)', 'comments']].head(1000))

# Download button
# We set a simple push button to prepare our download.
button = st.sidebar.beta_columns((1,3,1))
download = button[1].button("Prepare data for download")
# The value for the button will be False by default and will change to True when clicked.
# After that, our magic function will generate a download link and the link to download will show on screen.
if download:
    button[1].markdown(get_table_download_link(cases.head(1000)), unsafe_allow_html=True)

# Detailed case
# To show off some more posibilities, we will show a specific case.
# If a case number was chosen, that will be the selected case, obviously,
# otherwise, a case will be chosen randomly among those available
if case_number == "All":
    st.sidebar.header("Random case")
    cs = cases.sample().iloc[0]
else:
    st.sidebar.header(f"Case no. {case_number}")
    cs = cases

# Then we simply print the information of the case with a link to the original source of the data
# on the nuforc page
st.sidebar.text(f"{cs['datetime']}")
st.sidebar.text(f'{["Monday","Tuesday","Wednesday","Thurday","Friday","Saturday","Sunday"][cs["weekday"]]}')
st.sidebar.text(f"{cs['city']} -{cs['state']}- {cs['country']}")
st.sidebar.text(f"Duration: {cs['duration (hours/min)']}")
st.sidebar.markdown(f"{cs['comments'].capitalize()}")
st.sidebar.markdown(f"[Original Report]({cs['report_link']})")

######################################################
# Hope you have enjoyed our little dive on Streamlit #
# and the many possibilities of python! 🐍💻🍊        #
# Keep on coding!                                    #
#                           ferrero.felipe@gmail.com #
######################################################