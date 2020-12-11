from datetime import date, datetime, timedelta
from kaleido.scopes.plotly import PlotlyScope
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sodapy import Socrata
from typing import List, Tuple

# Data source/more info:
# https://dev.socrata.com/foundry/data.cdc.gov/9mfq-cb36
# ('https://data.cdc.gov/Case-Surveillance/United-States-'
#  'COVID-19-Cases-and-Deaths-by-State-o/9mfq-cb36')

# Get data.
client = Socrata('data.cdc.gov', None)
# Use None for public data set.
results = client.get('9mfq-cb36', limit=25000)
# May need to adjust limit as time goes on. (Original 20_000)

# Create and format DataFrame.
df = pd.DataFrame.from_records(results)
# Parse submission_date from str to date.
df['submission_date'] = pd.to_datetime(
    df['submission_date'], format='%Y-%m-%d'
    )
# Convert new_case and tot_cases columns to int.
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
    """Returns data from dataframe for a given date YYYY-MM-DD."""
    new_cases = df[df['submission_date'] == f'{date_str}']
    return new_cases


def create_fig(date_str: str, new=True):
    '''Returns a plotly go.Figure() for a given date YYYY-MM-DD
    for either new cases or total cases.'''
    cases = get_cases(date_str)
    if new:
        total = cases['new_case'].sum()
        scope = 'New'
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
    else:
        total = cases['tot_cases'].sum()
        scope = 'Total'
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
        title_text=f'{total:,} {scope} COVID-19 Cases - {full_date}',
        title_x=0.5,
        geo_scope='usa',
    )
    return fig


def plot_cases(date_str: str, new=True):
    '''Creates an interactive plot for either new/total cases
    for a given date YYYY-MM-DD.'''
    fig = create_fig(date_str, new)
    fig.show()


def save_fig(date_str, new=True):
    '''Saves either new/total plot for a given date YYYY-MM-DD
    as a .png file.'''
    if new:
        kind = 'new'
    else:
        kind = 'total'

    fig = create_fig(date_str, new)
    scope = PlotlyScope()
    with open(f'{kind}_cases/{date_str}_{kind}_cases.png', 'wb') as f:
        f.write(scope.transform(fig, format='png'))


def plot_new_all_dates():
    '''Plots new cases for all dates with a slider to select date.'''
    d_range = date_range(date(2020, 1, 22), (date.today() - timedelta(days=1)))

    fig = go.Figure()
    new_totals = []

    for dt in d_range:
        cases = df.query(f'submission_date == "{dt}"')
        new_totals.append(cases['new_case'].sum())
        fig.add_trace(
            go.Choropleth(
                locations=cases['state'],
                z=cases['new_case'],
                locationmode='USA-states',
                name='',
                visible=False,
                colorscale='reds',
                zmin=0,
                zmax=cases['new_case'].max() + 1,
                colorbar_title='Total Cases'
                )
        )

    fig.data[-1].visible = True

    steps = []
    for i in range(len(fig.data)):
        step = dict(
            method='update',
            label=d_range[i],
            args=[{'visible': [False] * len(fig.data)},
                  {'title': f"{new_totals[i]:,} New COVID-19 Cases - {datetime.strptime(d_range[i], '%Y-%m-%d').strftime('%B %d, %Y')}"}],
        )
        step['args'][0]['visible'][i] = True
        steps.append(step)

    sliders = [dict(
        active=len(steps) - 1,
        steps=steps,
        tickcolor='white',
        font={'color': 'white'}
    )]

    fig.update_layout(
        title_text=f"{new_totals[-1]:,} New COVID-19 Cases - {datetime.strptime(d_range[-1], '%Y-%m-%d').strftime('%B %d, %Y')}",
        title_x=0.5,
        geo_scope='usa',
        sliders=sliders
    )

    fig.show()


def calc_7_day_avg(column: Tuple):
    averages = []
    for x in range(len(column)):
        if x < 7:
            averages.append(round(sum(column[:x + 1]) / (x + 1)))
        else:
            averages.append(round(sum(column[x - 6:x + 1]) / 7))
    return averages


def state_line(state_abbr: str = None, df=df):
    '''Plot new cases vs. 7-day avg. If no state_abbr, plot entire country.'''
    # TODO: COMMENT
    # TODO: Look at negative values reported (throws off figure scale, eg.NY).
    if state_abbr is None:
        state_abbr = 'USA'
        state = df.groupby('submission_date', as_index=False)['new_case'].sum()
    else:
        state = df[df['state'] == state_abbr]

    new_cases = tuple(state['new_case'])
    state = state[['submission_date', 'new_case']]
    state['avg_7_day'] = calc_7_day_avg(new_cases)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=state['submission_date'],
                         y=state['new_case'],
                         name='New Cases')
                  )
    fig.add_trace(go.Scatter(x=state['submission_date'],
                             y=state['avg_7_day'],
                             name='7 Day Avg')
                  )
    fig.update_layout(title_text=f'COVID-19 in {state_abbr}',
                      title_x=0.5)
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='New Cases')
    fig.show()


if __name__ == '__main__':
    state_line()
    state_line('VA')
    plot_new_all_dates()
