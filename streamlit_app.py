import streamlit as st
import pandas as pd
import pydeck as pdk

import json

# Specify the path to your JSON file
file_path = 'massdotFreevalVolumeProfile_w_default_v4.json'

# Open and read the JSON file
with open(file_path, 'r') as file:
    jsondata = json.load(file)

# Read the Excel file
df = pd.read_excel("tcds_station_list.xlsx", sheet_name="tcds_list (2)", skiprows=11)

# Rename columns to match the expected names
df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}, inplace=True)

df["Station"] = df["Station"].astype(str)

data_list = []
for i in range(len(df["Station"])):
    if str(df["Station"][i]) in list(jsondata.keys()):
        data_list.append("Data")
    else:
        data_list.append("No Data")

df["Status"] = data_list

# Title of the Streamlit app
st.title("Location Data Visualization")

# Create filter options for the Route column
filter_options = ["All"] + sorted(df["Route"].unique().tolist())

# Option to filter the data based on the "Route" column
data_filter = st.selectbox("Select Route Filter", options=filter_options)

# Filter the DataFrame based on the selection
if data_filter != "All":
    filtered_df = df[df["Route"] == data_filter]
else:
    filtered_df = df

# Option to filter the data based on the "Route" column
color_filter = st.selectbox("Select Data Filter", options=["All", "Keep stations with no data", "Keep stations with data"])

if color_filter == "Keep stations with no data":
    filtered_df = filtered_df[filtered_df["Status"] == "No Data"]
elif color_filter == "Keep stations with data":
    filtered_df = filtered_df[filtered_df["Status"] == "Data"]
else:
    filtered_df = filtered_df

# Define color mapping based on the "status" column
color_map = {
    "No Data": [255, 0, 0],  # Red
    # "Partial": [0, 0, 255],  # Orange
    "Data": [0, 255, 0],  # Green
}

# Add a color column to the DataFrame based on the "status" column
filtered_df["color"] = filtered_df["Status"].map(color_map)


# Create a pydeck layer for the scatterplot (markers)
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_df,
    get_position=["longitude", "latitude"],
    get_fill_color="color",  # Fill color of the marker
    get_line_color=[0, 0, 0],  # Border color (black)
    get_radius=500,  # Adjust radius as needed
    pickable=True,
    radius_min_pixels=5,  # Minimum radius for the border
    radius_max_pixels=10,  # Maximum radius for the border
    stroked=True,  # Enable borders
)

# Checkbox to toggle marker labels
show_labels = st.checkbox("Show Marker Labels", value=True)

# Display filtered data in a table
st.write("Legend: Red-No Data, Green-Has Data")

# Create the list of layers to display on the map
layers = [scatter_layer]

# Conditionally add the text layer based on the checkbox
if show_labels:
    text_layer = pdk.Layer(
        "TextLayer",
        data=filtered_df,
        get_position=["longitude", "latitude"],
        get_text="Station",  # Replace with the name of the column you want to use as labels
        get_color=[0, 0, 0, 200],  # Black text with some transparency
        get_size=16,
        get_alignment_baseline="'bottom'",
    )
    layers.append(text_layer)

# Set the initial view of the map
view_state = pdk.ViewState(
    latitude=filtered_df["latitude"].mean(),
    longitude=filtered_df["longitude"].mean(),
    zoom=8,
    pitch=0,
)

# Display the map with the selected layers
st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/streets-v11"   # Street view basemap
))



# Display filtered data in a table
st.write("Filtered Data", filtered_df)

# Display the entire dataframe as a table
st.write("Complete Dataset", df)
