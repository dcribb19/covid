from datetime import date, datetime, timedelta
from kaleido.scopes.plotly import PlotlyScope
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sodapy import Socrata
from typing import List
from covid import calc_7_day_avg

# Data source/more info:
# https://dev.socrata.com/foundry/data.virginia.gov/bre9-aqqr
# ('https://data.virginia.gov/Government/VDH-COVID-19-'
#  'PublicUseDataset-Cases/bre9-aqqr')

# Get data.
client = Socrata('data.virginia.gov', None)
# Use None for public data set.
results = client.get('bre9-aqqr', limit=50000)
# May need to adjust limit as time goes on.
# 10/29 - VA has 31_100 rows

# Create and format DataFrame.
df = pd.DataFrame.from_records(results)
# Parse submission_date from str to date.
df['report_date'] = pd.to_datetime(
    df['report_date'], format='%Y-%m-%d'
    )
# Convert and total_case column to int.
df['total_cases'] = df['total_cases'].astype(int)


def locality_line(localities: list, df=df):
    '''Plot total cases vs. 7-day avg.'''
    fig = go.Figure()

    for locality in localities:
        locality_df = df[df['locality'] == locality]

        fig.add_trace(go.Scatter(x=locality_df['report_date'],
                                 y=locality_df['total_cases'],
                                 name=locality)
                      )

    fig.update_layout(title_text='COVID-19 in VA',
                      title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Total Cases')
    fig.show()


def _add_new_cases(locality: str, df):
    '''Add a new_cases column df for locality.'''
    df = df[df['locality'] == locality]
    df['new_cases'] = df['total_cases'].diff(periods=-1).fillna(0).astype(int)
    return df


def plot_new_cases(df):
    '''COMMENT'''
    # TODO: Look at negative values reported (throws off figure scale, eg.NY).
    fig = go.Figure()

    arl = _add_new_cases('Arlington', df)
    fairfax = _add_new_cases('Fairfax', df)
    loudoun = _add_new_cases('Loudoun', df)
    c_field = _add_new_cases('Chesterfield', df)

    fig.add_trace(go.Bar(x=fairfax['report_date'],
                         y=fairfax['new_cases'],
                         name='Fairfax')
                  )
    fig.add_trace(go.Bar(x=arl['report_date'],
                         y=arl['new_cases'],
                         name='Arlington')
                  )
    fig.add_trace(go.Bar(x=c_field['report_date'],
                         y=c_field['new_cases'],
                         name='Chesterfield')
                  )
    fig.add_trace(go.Bar(x=loudoun['report_date'],
                         y=loudoun['new_cases'],
                         name='Loudoun')
                  )
    '''
    fig.add_trace(go.Scatter(x=state['submission_date'],
                             y=state['avg_7_day'],
                             name='7 Day Avg')
                  )
    '''
    fig.update_layout(barmode='stack',
                      title_text='COVID-19 in VA',
                      title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='New Cases')
    fig.show()


if __name__ == '__main__':
    # locality_line(['Arlington', 'Chesterfield', 'Charlottesville',
    #               'Fairfax', 'Loudoun'])
    plot_new_cases(df)
