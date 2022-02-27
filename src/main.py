import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
from plotly.subplots import make_subplots

import os
print(os.getcwd())

if os.getcwd() == "/Users/ozgunhaznedar/Desktop/swiss_renewable_energy_app":
    os.chdir('src')
print(os.getcwd())
#####################################################################################################################
@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

with open("../data/georef-switzerland-kanton.geojson") as response:
    geo = json.load(response)



df_raw = load_data(path="../data/renewable_power_plants_CH.csv")
df = deepcopy(df_raw)


# from wikipedia : dictionary of canton names and codes
df_cc_raw = load_data(path="../data/canton_codes.csv")
df_cc = deepcopy(df_cc_raw)

codes = dict(zip(df_cc.iloc[0], df_cc.iloc[1]))

# adding the kan_name column
df["kan_name"] = df.canton.apply(lambda x: codes.get(x, "hata"))

#groupby canton
df_gb_canton = df.groupby("kan_name").agg(
    {"electrical_capacity": "sum", "production": "sum"}
)
df_gb_canton.reset_index(inplace=True)


df_gb = df.groupby(["kan_name", "energy_source_level_2"]).agg(
    {"electrical_capacity": "sum", "production": "sum"}
)

df_gb2 = df_gb.reset_index(drop=False, level="energy_source_level_2")

df_pvt = df_gb.reset_index().pivot(
    columns="energy_source_level_2",
    index="kan_name",
    values="production",
)
df_pvt["Total"] = df_pvt.sum(axis=1)
df_pvt.sort_values(by="Total", ascending=True, inplace=True)

df_e = df.groupby("energy_source_level_2").agg(
    {"electrical_capacity": "sum", "production": "sum"}
)
#####################################################################################################################


# adding the kan_name column
# exec(open("canton_names.py").read())

# Add title and header
st.title("Renewable Energy Production in Switzerland")
st.header("Energy Production by Cantons (MWH) ")

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=df)
    #st.table(data=df)

fig = go.Figure(
    go.Choroplethmapbox(
        geojson=geo,
        locations=df_gb_canton.kan_name,
        featureidkey="properties.kan_name",
        z=df_gb_canton.production,
        colorscale="Cividis",
        # zmin=0,
        # zmax=500000,
        marker_opacity=0.5,
        marker_line_width=0,
    )
)
fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=6.3,
    mapbox_center={"lat": 46.8, "lon": 8.5},
    width=800,
    height=600,
)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig)



fig4 = go.Figure()
for energy in ["Bioenergy", "Hydro", "Solar", "Wind"]:
    fig4.add_trace(
        go.Bar(
            y=df_pvt.index,
            x=df_pvt[energy],
            hovertemplate="%{x:.2f}",
            # showlegend=False,
            name=energy,
            orientation="h",
        ),
    )
fig4.update_layout(barmode="stack")
fig4.update_layout(
    paper_bgcolor="#bcbcbc",
    plot_bgcolor="#f9e5e5",
    width=800,
    height=600,
    title="Renewable Electricity Production by Canton (MWH)",
)

energy="Solar"
fig7 = go.Figure()
fig7.add_trace(
    go.Bar(
        y=df_pvt.sort_values(by=energy, ascending=True).index,
        x=df_pvt.sort_values(by=energy, ascending=True)[energy],
        hovertemplate="%{x:.2f}",
        # showlegend=False,
        name=energy,
        orientation="h",
    ),
)
fig7.update_layout(
    paper_bgcolor="#bcbcbc",
    plot_bgcolor="#f9e5e5",
    width=800,
    height=600,
    title=f"{energy} Energy Production by Canton (MWH)",
)

# Setting up columns
left_column, right_column = st.columns([3, 1])

# Widgets: selectbox
sources = ["All"]+sorted(pd.unique(df['energy_source_level_2']))
energy = left_column.selectbox("Choose Energy Source", sources)



if energy == "All":
    st.plotly_chart(fig4)
else:
    st.plotly_chart(fig7)




fig5 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Electrical Capacity in MW", "Production in MWH"),
)
fig5.add_trace(
    go.Bar(
        x=df_e.index,
        y=df_e.electrical_capacity,
        hovertemplate="%{y:.0f} MW",
        marker_color=["#3d85c6", "#29be8a", "#ffff00", "#bce954"],
        showlegend=False,
        text=round(df_e.electrical_capacity, 0),
    ),
    row=1,
    col=1,
)
fig5.add_trace(
    go.Bar(
        x=df_e.index,
        y=df_e.production,
        hovertemplate="%{y:.0f} MWH",
        marker_color=["#3d85c6", "#29be8a", "#ffff00", "#bce954"],
        showlegend=False,
        text=round(df_e.production / 1000000, 3),
    ),
    row=1,
    col=2,
)
fig5.update_layout(
    paper_bgcolor="#bcbcbc",
    plot_bgcolor="#f9e5e5",
    width=800,
    height=500,
    title="Energy from Renewable Resources",
)

canton = "Zug"
fig6 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Electrical Capacity in MW", "Production in MWH"),
)
fig6.add_trace(
    go.Bar(
        x=df_gb2.loc[canton].energy_source_level_2,
        y=df_gb2.loc[canton].electrical_capacity,
        hovertemplate="%{y:.1f} MW",
        marker_color=["#3d85c6", "#29be8a", "#ffff00", "#bce954"],
        showlegend=False,
        text=round(df_gb2.loc[canton].electrical_capacity, 1),
    ),
    row=1,
    col=1,
)
fig6.add_trace(
    go.Bar(
        x=df_gb2.loc[canton].energy_source_level_2,
        y=df_gb2.loc[canton].production,
        hovertemplate="%{y:.0f} MWH",
        marker_color=["#3d85c6", "#29be8a", "#ffff00", "#bce954"],
        showlegend=False,
        text=round(df_gb2.loc[canton].production / 1, 0),
    ),
    row=1,
    col=2,
)
fig6.update_layout(
    paper_bgcolor="#bcbcbc",
    plot_bgcolor="#f9e5e5",
    width=800,
    height=500,
    title="Energy from Renewable Resources",
)
fig6.update_layout(barmode="stack")

# Setting up columns
left_column2, right_column2 = st.columns([3, 1])

cantons = ["All"]+sorted(pd.unique(df['canton']))
canton = left_column2.selectbox("Choose Canton", cantons)

if canton == "All":
    st.plotly_chart(fig5)
else:
    st.plotly_chart(fig6)

