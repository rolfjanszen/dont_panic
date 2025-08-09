from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from os.path import isfile, expanduser

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash()
#display an image
image_path = app.get_asset_url('logo.webp')

app.layout = html.Div([
    html.Div([
        html.H1(children='Dashboard    ', style={'textAlign': 'center'}),
        html.Img(src=image_path, width='4%', height='4%', style={'display': 'flex', 'margin': 'auto'}),
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between'}),
    dcc.Dropdown(df.country.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    dff = df[df.country==value]
    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True, dev_tools_hot_reload=True)
