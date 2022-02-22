import pandas as pd
from urllib.request import urlopen
import json
import pandas as pd
from copy import deepcopy

@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df


with open("../data/raw/georef-switzerland-kanton.geojson") as json_file:
    geo = json.load(json_file)
df_raw = load_data(path="../data/raw/renewable_power_plants_CH.csv")
df = deepcopy(df_raw)



# from wikipedia : dictionary of canton names and codes
df_cc = pd.read_csv("../data/raw/canton_codes.csv")
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