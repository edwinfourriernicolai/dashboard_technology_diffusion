import streamlit as st
import pandas as pd
import altair as alt
import myfct

# Set the title
st.title("Diffusion of digital technologies")

# Directory path
#dirpath = 'C:/Edwin/Communication/Dashboards/technology_exposure/'


### Prepare data

# Import the concordance CPC-NACE
cpc_nace_df = pd.read_csv("concordance_cpc_nace.csv", sep=";", dtype={'cpc': 'object', 'nace': 'object', 'weight': 'float64'})
# Import patent data
patent_df = pd.read_csv("selected_patent_all.csv", sep=';')
# Import the list of NACE
nace_df = pd.read_csv('nace_v2.csv', sep=';', dtype={'Level': 'int64', 'Code': 'object', 'Code': 'object'})

# Convert date strings to datetime objects
patent_df["publication_date"] = pd.to_datetime(patent_df["publication_date"], format="%Y%m%d")
# Get the list of NACE codes
nace_l = nace_df.loc[(nace_df['Level'] == 4), 'Code'].to_list()
# Create a dictionary of sectors
sector_dict = nace_df[(nace_df['Level'] == 4)].set_index("Description")["Code"].to_dict()
# Create a dictionary of sector names
sector_names = {
    "A": "Agriculture, forestry and fishing",
    "B": "Mining and quarrying", 
    "C": "Manufacturing", 
    "D": "Electricity, gas, steam and air conditioning supply",
    "E": "Water supply; sewerage, waste management and remediation activities", 
    "F": "Construction", 
    "G": "Wholesale and retail trade; repair of motor vehicles and motorcycles", 
    "H": "Transportation and storage",
    "I": "Accommodation and food service activities", 
    "J": "Information and communication", 
    "K": "Financial and insurance activities",
    "L": "Real estate activities", 
    "M": "Professional, scientific and technical activities", 
    "N": "Administrative and support service activities",
    "O": "Public administration and defence; compulsory social security", 
    "P": "Education", 
    "Q": "Human health and social work activities",
    "R": "Arts, entertainment and recreation", 
    "S": "Other service activities", 
    "T": "Activities of households as employers; undifferentiated goods and services producing activities of households for own use",
    "U": "Activities of extraterritorial organisations and bodies",
}


### Sidebar

topic_list = ["robotics", "virtual reality", "big data", "internet of things", "cybersecurity"]
sector_list = list(sector_dict.keys())
with st.sidebar:
    selected_topic = st.selectbox("Select a technological domain", topic_list)
    selected_date = st.slider('Select a time range', 1990, 2014, (1990, 2014))
    selected_sector_des = st.selectbox("Select an economic sector", sector_list)

# Get the code of the sector instead of the description
selected_sector = sector_dict[selected_sector_des]

# Filter data based on the selected filters
filtered_df = patent_df[(patent_df["topic"] == selected_topic)]
filtered_df = filtered_df[(filtered_df["publication_date"].dt.year >= selected_date[0]) & (filtered_df["publication_date"].dt.year <= selected_date[1])]


### Computations

#filtered_df = patent_df.copy()
#selected_date = (1990,2005)
#selected_sector = '96.09'

# if filtered_df has changed -> affect cache?
# select years after 

# Count the number of patents by NACE sector for each year
count_l = []
for year in range(selected_date[0], selected_date[1]+1):
    count_y = myfct.count_patent_nace(nace_l, filtered_df[(filtered_df["publication_date"].dt.year == year)], cpc_nace_df)
    count_y['year'] = year
    count_l.append(count_y)
# Convert the list of yearly dictionaries into a longitudinal dataframe
count_df_l = [pd.DataFrame(count_y, index=[0]) for count_y in count_l]
count_df = pd.concat(count_df_l, ignore_index=True)
count_df.set_index("year", inplace=True)
count_df = count_df.transpose()


### Construct plots

## Evolution of patents published over time
# Group by year and count the number of patents for each year
grp_year_df = filtered_df.groupby(filtered_df["publication_date"].dt.year).size().reset_index(name="number_of_patents")
# Plot
topic_ts_chart = (
    alt.Chart(grp_year_df)
    .mark_line()
    .encode(
        x=alt.X("publication_date:O", axis=alt.Axis(title="Year")),
        y=alt.Y("number_of_patents:Q", axis=alt.Axis(title="Number of patents")),
        tooltip=[alt.Tooltip("number_of_patents:Q", title="Number of patents"), alt.Tooltip("year:O", title="Year")],
    )
    .properties(title="Number of patents published for {} over time".format(selected_topic))
)

## Patents by country
# Group by country and count the number of patents for each country
grp_country_df = filtered_df.groupby(filtered_df["country"]).size().reset_index(name="number_of_patents")
# Select only the top 10 countries
grp_country_df = grp_country_df.nlargest(10, "number_of_patents")
# Plot
country_bp_chart = (
    alt.Chart(grp_country_df)
    .mark_bar()
    .encode(
        x=alt.X("number_of_patents", axis=alt.Axis(title="Number of patents")),
        y=alt.Y("country", axis=alt.Axis(title="Country")).sort('-x'),
        tooltip=[alt.Tooltip("number_of_patents:Q", title="Number of patents"), alt.Tooltip("country:N", title="Country")],
        color=alt.Color("country:N", legend=None),        
    )
    .properties(title="Top 10 countries with the highest number of patents published for {}".format(selected_topic))
)

## Evolution of selected sector exposure over time
# Extract data for the selected sector
count_sector = count_df.loc[selected_sector].reset_index(name="number_of_patents")
# Plot
sector_ts_chart = (
    alt.Chart(count_sector)
    .mark_line()
    .encode(
        x=alt.X("year:O", axis=alt.Axis(title="Year")),
        y=alt.Y("number_of_patents:Q", axis=alt.Axis(title="Number of patents")),
        tooltip=[alt.Tooltip("number_of_patents:Q", title="Number of patents"), alt.Tooltip("year:O", title="Year")],
    )
    .properties(title="Number of patents published for {} in the {} sector over time".format(selected_topic, selected_sector))
)

## Sector exposure
# Compute the total over the period
tot_count_sector = count_df.sum(axis=1).reset_index()
tot_count_sector.columns = ["nace_4d", "number_of_patents"]
# Group by economic sector (1 digit)
tot_count_sector["nace_1d"] = tot_count_sector["nace_4d"].apply(myfct.determine_nace_1d)
grp_sector_df = tot_count_sector.groupby("nace_1d", as_index=False)["number_of_patents"].sum()
grp_sector_df["name"] = grp_sector_df["nace_1d"].map(lambda sector: sector_names[sector])
# Plot
sector_bp_chart = (
    alt.Chart(grp_sector_df)
    .mark_bar()
    .encode(
        y=alt.Y("number_of_patents:Q", axis=alt.Axis(title="Number of patents")),
        x=alt.X("name:N", axis=alt.Axis(title=None, labelLimit=250)),
        tooltip=[alt.Tooltip("number_of_patents:Q", title="Number of patents"), alt.Tooltip("name:N", title="Sector")],
        color=alt.Color("name:N", legend=None),
    )
    .properties(title="Number of patents published for {} by economic sector".format(selected_topic))
)


### Display the charts

#combined_chart = alt.vconcat(alt.hconcat(topic_ts_chart, country_bp_chart),alt.hconcat(sector_bp_chart, sector_ts_chart))
combined_chart = alt.vconcat(topic_ts_chart, country_bp_chart, sector_bp_chart, sector_ts_chart)
st.altair_chart(combined_chart)


### Methodology

st.header("Methodology")
st.write("Our methodology proposes to track the diffusion of some digital technologies in the economy. "
         "In this attempt, we classify patents from the Google Public Patent database by technological domain based on their Cooperative Patent Classification (CPC) codes and textual analysis. "
         "In particular, we use the classification provided by Ménière et al. (2020) for identifying the CPC codes for big data, virtual reality and cybersecurity technologies whereas we use the former U.S. patent classification (USPC) class 901 and the junction CPC group Y10S901 to identify patents related to robots. "
         "To identify CPC codes for the internet of things, we use the classification provided by IPO (2014) as well as other relevant groups sampled from the literature. "
         "We select only patents containing at least one of a set of predetermined keywords in either their title or their abstract among the patents found in the relevant CPC groups for each technological domain. "
         "When the same patent is published in multiple offices, we keep only that with the earliest publication date. "
         "Patents are related to NACE sectors using the concordance between the CPC and the International Standard Industrial Classification (ISIC) (itself matched to the NACE classification) provided by Lybbert \& Zolas (2014).")

st.subheader("References")
st.markdown("- Lybbert, T. J. and Zolas, N. J. (2014). Getting patents and economic data to speak to each other: An ‘Algorithmic Links with Probabilities’ approach for joint analyses of patenting and economic activity. Research Policy, 43(3):530–542.")
st.markdown("- IPO (2014). Eight Great Technologies: The Internet of Things. Technical report, UK Intellectual Property Office, Newport, United-Kingdom.")
st.markdown("- Ménière, Y., Philpott, J., Pose Rodriguez, J., Rudyk, I., Wewege, S., and Wienold, N. (2020). Patents and the Fourth Industrial Revolution: The global technology trends enabling the data-driven economy. Technical report, European Patent Office, Munich, Germany.")


### About us

st.header("About us")
st.write("This dashboard is based on a methodology developed by:")
st.write("- Mauro Caselli, School of International Studies \& Dep. of Economics and Management, University of Trento, Italy")
st.write("- Edwin Fourrier-Nicolaï, School of International Studies \& Dep. of Economics and Management, University of Trento, Italy")
st.write("- Andrea Fracasso, School of International Studies \& Dep. of Economics and Management, University of Trento, Italy")
st.write("- Sergio Scicchitano, John Cabot University, Rome, National Institute for Public Policies Analysis (INAPP), Italy, and Global Labor Organisation (GLO), Germany")

st.write("Contact: fourrier.edwin@gmail.com")