import streamlit as st
import pandas as pd
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pytz
from io import BytesIO

PR_TIME_ZONE = pytz.timezone("Etc/GMT+4")

date_from_str = "2021-10-27"
date_to_str = "2021-10-30"

date_from = datetime.datetime.strptime(date_from_str,'%Y-%m-%d')
date_to = datetime.datetime.strptime(date_to_str,'%Y-%m-%d')

# Useful Functions
def utcToPrTime(series):
    return pd.to_datetime(series).dt.tz_localize('UTC').dt.tz_convert(PR_TIME_ZONE)


def localizePrTime(series):
    return pd.to_datetime(series).dt.tz_localize(PR_TIME_ZONE)


@st.cache()
def readAllPopulation():
    all_days_population = {}
    cur_date = date_from
    while(cur_date <= date_to):
        ds = cur_date.strftime("%Y-%m-%d")
        print("Loadin for:",ds)
        temp=pd.read_csv(f"population/population_{ds}.csv")
        # Data is already in PR Timezone
        temp['postedDate']=localizePrTime(temp['postedDate'])
        temp['day'] = ds

        all_days_population[ds]=temp

        cur_date = cur_date +datetime.timedelta(days=1)


    return list(all_days_population.keys()), pd.concat(all_days_population.values())

@st.cache()
def readAllSampled():
    all_days_sampled = {}
    cur_date = date_from
    while(cur_date <= date_to):
        ds = cur_date.strftime("%Y-%m-%d")
        print("Loadin for:",ds)
        temp=pd.read_csv(f"sampled/sampled_oil_{ds}.csv")
        temp['postedDate'] = utcToPrTime(temp['intake_date'])
        temp['day'] = ds

        all_days_sampled[ds] = temp

        cur_date = cur_date +datetime.timedelta(days=1)
        
    return list(all_days_sampled.keys()), pd.concat(all_days_sampled.values())


def plotTimeSeries(selectedPopulation,selectedSampled):

    population_ts = selectedPopulation \
        .set_index(pd.DatetimeIndex(selectedPopulation['postedDate'])) \
        .resample('1min').size().reset_index(name='count')
    
    sampled_ts = selectedSampled \
        .set_index(pd.DatetimeIndex(selectedSampled['postedDate'])) \
        .resample('1min').size().reset_index(name='count')

    fig = plt.figure(figsize = (15,8))
    sns.lineplot(x = 'postedDate', y = 'count',data = population_ts)
    sns.lineplot(x = 'postedDate', y = 'count',data = sampled_ts)
    plt.xlabel("Posted Date")
    plt.ylabel("Tweets per minute")
    plt.legend(["Population","Sampled"])
    
    
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)
    #st.pyplot(fig)

st.set_page_config(layout='wide')
st.title("Gnip Sampling Visualization")

keys1, all_population = readAllPopulation()

keys2, all_sampled = readAllSampled()

if ",".join(keys1) != ",".join(keys2):
    print("ERR:", "Dates for Population and Sampled datasets do not match")
    print("Population:",keys1)
    print("Sampled:",keys2)
    raise Error("Incomplete Data")

all_keys = ["All"]
all_keys.extend(keys1)

selection = st.sidebar.selectbox('Select Date',all_keys)

if selection != "All":
    selectedPopulation = all_population[all_population['day']==selection]
    selectedSampled = all_sampled[all_sampled['day']==selection]
else:
    selectedPopulation = all_population
    selectedSampled = all_sampled

plotTimeSeries(selectedPopulation,selectedSampled)

