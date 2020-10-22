from datetime import date, datetime, timedelta
from typing import List
from kaleido.scopes.plotly import PlotlyScope
import pandas as pd
import plotly.graph_objects as go
from sodapy import Socrata
import plotly.express as px

# More info:
# https://dev.socrata.com/foundry/data.cdc.gov/9mfq-cb36
# ('https://data.cdc.gov/Case-Surveillance/United-States-'
#  'COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36')


# Get data.
client = Socrata('data.cdc.gov', None)
# Use None for public data set.
results = client.get('9mfq-cb36', limit=20000)
# May need to adjust limit as time goes on. (Original 20_000)

# Create and format DataFrame.
df = pd.DataFrame.from_records(results)
# Parse submission_date from str to date.
df['submission_date'] = pd.to_datetime(
    df['submission_date'], format='%Y-%m-%d'
    )

df['new_case'] = df['new_case'].astype(float).astype(int)
df['tot_cases'] = df['tot_cases'].astype(int)


def date_range(start_date: date, end_date: date) -> List[str]:
    '''Return a list of dates YYYY-MM-DD between 2 dates.'''
    if not all(isinstance(dt, date) for dt in [start_date, end_date]):
        raise TypeError('Input must be date type.')

    if end_date < start_date:
        raise ValueError('Start date must be before end date.')

    if start_date < date(2020, 1, 22):
        raise ValueError(('Start date is out of range.'
                          'Start date for dataset is 2020-01-22.'))

    return [(start_date + timedelta(x)).strftime('%Y-%m-%d')
            for x in range((end_date - start_date).days + 1)]


def get_cases(date_str: str, df=df):
    """Return data for a given date 'YYYY-MM-DD'"""
    new_cases = df[df['submission_date'] == f'{date_str}']
    return new_cases


def create_fig(date_str: str, total: str):
    if total not in ['new', 'total']:
        raise ValueError("total must be 'new' or 'total'.")

    cases = get_cases(date_str)
    if total == 'new':
        fig = go.Figure(data=go.Choropleth(
            locations=cases['state'],
            z=cases['new_case'],
            locationmode='USA-states',
            colorscale=px.colors.sequential.Reds,
            zmin=0,
            zmax=cases['new_case'].max() + 1,  # + 1 in case max == 0.
            colorbar_title='Total Cases'
            )
        )
    else:  # total == 'total'
        fig = go.Figure(data=go.Choropleth(
            locations=cases['state'],
            z=cases['tot_cases'],
            locationmode='USA-states',
            colorscale=px.colors.sequential.matter,
            colorbar_title='Total Cases'
            )
        )

    full_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%B %d, %Y')
    fig.update_layout(
        title_text=f'{total.title()} COVID-19 Cases - {full_date}',
        title_x=0.5,
        geo_scope='usa',
    )
    return fig


def plot_new_cases(date_str: str):
    fig = create_fig(date_str, total='new')
    fig.show()


def plot_total_cases(date_str: str):
    fig = create_fig(date_str, total='total')
    fig.show()


def save_new_fig(date_str):
    '''Saves figure as a png file.'''
    fig = create_fig(date_str, total='new')
    scope = PlotlyScope()
    with open(f'new_cases/{date_str}_new_cases.png', 'wb') as f:
        f.write(scope.transform(fig, format='png'))


def save_total_fig(date_str):
    '''Saves figure as a png file.'''
    fig = create_fig(date_str, total='total')
    scope = PlotlyScope()
    with open(f'total_cases/{date_str}_total_cases.png', 'wb') as f:
        f.write(scope.transform(fig, format='png'))
