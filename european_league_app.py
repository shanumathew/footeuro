import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import storage
from PIL import Image
from io import BytesIO

# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = storage.Client(credentials=credentials)

# Retrieve file contents.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def read_file(bucket_name, file_path):
    bucket = client.bucket(bucket_name)
    content = bucket.blob(file_path).download_as_string()
    return content

bucket_name = "streamlit-datasets"

with st.sidebar:
    st.title('Eurpoean soccer leagues')


year_selection = st.sidebar.selectbox(
    "year",
    ("21-22", "22-23")
)

country = st.sidebar.selectbox(
    "Country",
    ("ITA", "ENG","GER","ESP","FRA")
)

if year_selection == "21-22": 
    file_path = "euro_league_datasets/2021-2022 Football Team Stats.csv"
else:
    file_path = "euro_league_datasets/2022-2023 Football Team Stats.csv"


table_teams= read_file(bucket_name, file_path)
df_teams = pd.read_csv(BytesIO(table_teams),sep=';',encoding='ISO-8859-1')

country_input = country
df_teams_country = df_teams[df_teams.Country == country_input]

if year_selection == "21-22": 
    df_teams_country['Pts/MP'] = df_teams_country['Pts']/df_teams_country['MP']

df_teams_country = df_teams_country[['LgRk','Squad','MP','W','D','L','GF','GA','GD','Pts','Pts/MP']].sort_values('LgRk')
#df_teams = pd.read_csv('gs://streamlit-datasets/euro_league_datasets/2021-2022 Football Player Stats.csv',sep=';',encoding='ISO-8859-1')
#print(df_teams)
#df_teams_country = df_teams_country.reindex(df_teams_country['LgRk'])

hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('LgRk : League Rank')
    st.markdown('MP : Matches Played')
    st.markdown('W : Win')
    st.markdown('D : Draw')
    st.markdown('L : Lose')
    st.markdown('GF : Goal For')
    st.markdown('GA : Goal Against')
    st.markdown('GD : Goal Difference')
    st.markdown('Pts : Points')   
    st.markdown('Pts/MP : Average Points per Match')   

flag = Image.open(f'flag_images/{country}.png')        
st.image(flag)

st.table(df_teams_country)
