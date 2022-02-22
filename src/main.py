import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy
from plotly.subplots import make_subplots

a = "afadsf"
print(a)

# First some MPG Data Exploration
@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

df_raw = load_data(path="/Users/ozgunhaznedar/Desktop/SIT/my-first-streamlitapp/data/raw/renewable_power_plants_CH.csv")
df = deepcopy(df_raw)

#adding the kan_name column
exec(open("/Users/ozgunhaznedar/Desktop/SIT/my-first-streamlitapp/src/canton_names.py").read())

# Add title and header
st.title("Renewable Energy Production in Switzerland")
st.header("Energy Production by Cantons ")

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=df)
    #st.table(data=df)

# Setting up columns
left_column, middle_column, right_column = st.columns([3, 1, 1])

# Widgets: selectbox
cantons = ["All"]+sorted(pd.unique(df['canton']))
canton = left_column.selectbox("Choose a Canton", cantons)

# Widgets: radio buttons
show_sums = middle_column.radio(
    label='Show Total Production', options=['Yes', 'No'])

plot_types = ["Matplotlib", "Plotly"]
plot_type = right_column.radio("Choose Plot Type", plot_types)

# Flow control and plotting
if canton == "All":
    reduced_df = df
else:
    reduced_df = df[df["canton"] == canton]

sums = reduced_df.groupby('production').sum()

# In Matplotlib
m_fig, ax = plt.subplots(1, 1, figsize=(10, 6))
df_e.loc[df_e.index, "production"].sort_values(ascending=False).plot.bar(ax=ax)

ax.set_title("Energy Production by Source")
ax.set_xlabel('Source')
ax.set_ylabel('MWH')

# In Plotly
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

# Select which plot to show
if plot_type == "Matplotlib":
    st.pyplot(m_fig)
else:
    st.plotly_chart(fig5)
