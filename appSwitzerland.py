import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
#check different leafmap backends
import leafmap.foliumap as leafmap


st.set_page_config(layout="wide")

# load geojson file of Switzerland
gdf = gpd.read_file("data/chf.geojson")


@st.cache
def load_telegram_data():
    """
    load data with clusters results, after qualitative analysis
    """
    df = pd.read_csv("data/df_prep.csv")
    return df


def create_df_value_counts(df):
    """
    prepare data for plotting
    :df: dataframe with cluster results
    """
    messages_per_week_dict = dict(df.value_counts("week"))
    df_value_counts = df.value_counts(["cluster_names", "week"]).reset_index()
    df_value_counts.columns = ["cluster_names", "week", "occurence_count"]
    return df_value_counts

def modify_df_for_table(df_mod, region_select, cluster_select, week_slider):
    """
    modify dataframe for based on user input
    
    :df_mod: dataframe with cluster results
    :region_select: selected region
    :cluster_select: selected cluster
    :week_slider: selected week range
    """
    if region_select!="all Cantons":
        df_mod = df_mod[df_mod.region==region_select]
    if not "all found clusters" in cluster_select:
        df_mod = df_mod[df_mod.cluster_names.isin(cluster_select)]
    df_mod = df_mod[df_mod.week.between(week_slider[0], week_slider[1])]
    df_mod = df_mod[["chat", "messageText", "cluster_names", "messageDatetime", "week"]]
    return df_mod

# load data
df = load_telegram_data()

# title for the app
st.title('R2G: Automatic Bottom-Up Identification of Refugee Needs via Telegram')

# create 3 columns for menu selection
text_col1, text_col2, text_col3  = st.columns(3)

# create select box for canton of interest
with text_col1:
    regions = df.region.unique().tolist()
    region_select = st.selectbox(
        "Select a canton of interest",
        regions,
        )

# create multiselect for cluster/clusters of interest
with text_col2:
    cluster_names = df.cluster_names.unique().tolist()
    cluster_names = ["all found clusters"] + cluster_names 
    cluster_select = st.multiselect(
        'Choose the topic of interest',
        cluster_names,
        ["all found clusters"]
        )

# create slider for week of interest
with text_col3:    
    week_slider = st.slider('Choose calendar week of interest',
        min_value=int(df.week.min()), 
        value=(int(df.week.min()), int(df.week.max())), 
        max_value=int(df.week.max())
        )

# use functions to modify dataframe based on user input
df_mod = modify_df_for_table(df_mod=df, region_select=region_select, cluster_select=cluster_select, week_slider=week_slider)
df_value_counts = create_df_value_counts(df=df_mod)    

# create 2 columns for visualisation
visual_col1, visual_col2= st.columns(2)

# column 1: map
with visual_col1:
    # create map for all cantons
    if region_select=="all Cantons":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf, layer_name="Cantons", fill_colors=["red"])
        m.to_streamlit()

    # create map for selected canton
    if region_select!="all Cantons":
        m = leafmap.Map(center=[46.449212, 7.734375], zoom=7)
        m.add_gdf(gdf[gdf["NAME_1"]!=region_select], layer_name="Cantons", fill_colors=["blue"])
        m.add_gdf(gdf[gdf["NAME_1"]==region_select], layer_name="Canton choosen for Analysis", fill_colors=["red"])
        m.to_streamlit()

# column 2: line chart representing the clusters over time
with visual_col2:
    st.text(f'We identified the following clusters within {region_select}')
    fig = px.line(df_value_counts[df_value_counts.cluster_names != "no_class"].sort_values(['week']), x="week", y="occurence_count", color='cluster_names', title='Cluster over time', width=1000, height=600)
    st.plotly_chart(fig, use_container_width=True) 
    
# st.dataframe(df_mod) within the production app we decided to not show the dataframe, including the messages

