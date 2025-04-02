# FIFA World Cup Dashboard

import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# Step 1: Create Dataset
url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
df = pd.read_html(url, match="Year")[0]

# Standardizing column names
df.columns = ['Year', 'Winners', 'Score', 'Runners-up', 'Venue', 'Attendance']
df = df[['Year', 'Winners', 'Runners-up']]

# Convert Year to integer for consistency
df['Year'] = pd.to_numeric(df['Year'], errors='coerce').dropna().astype(int)

# Standardizing country names
df.replace({'West Germany': 'Germany'}, inplace=True)

# Count total wins per country
win_counts = df['Winners'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

# Step 2: Create Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard"),
    
    # Choropleth Map
    dcc.Graph(id='choropleth-map'),
    
    # Dropdown to select a country
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': country, 'value': country} for country in win_counts['Country']],
        placeholder='Select a country'
    ),
    html.Div(id='country-stats'),
    
    # Dropdown to select a year
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
        placeholder='Select a year'
    ),
    html.Div(id='year-stats')
])

# Callbacks
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('choropleth-map', 'id')
)
def update_map(_):
    fig = px.choropleth(
        win_counts, 
        locations="Country", 
        locationmode="country names",
        color="Wins", 
        title="World Cup Wins by Country",
        color_continuous_scale=px.colors.sequential.Plasma
    )
    return fig

@app.callback(
    Output('country-stats', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_stats(selected_country):
    if not selected_country:
        return ""
    wins = win_counts.loc[win_counts['Country'] == selected_country, 'Wins'].values
    return f"{selected_country} has won {wins[0]} World Cup(s)." if len(wins) > 0 else "No data available."

@app.callback(
    Output('year-stats', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_stats(selected_year):
    if not selected_year:
        return ""
    row = df[df['Year'] == selected_year]
    if row.empty:
        return "No data available for this year."
    row = row.iloc[0]
    return f"In {selected_year}, {row['Winners']} won and {row['Runners-up']} was the runner-up."

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0", port=8080)
