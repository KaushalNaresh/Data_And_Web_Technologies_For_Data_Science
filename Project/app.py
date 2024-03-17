import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

demography_data = pd.read_csv('demography_data.csv', index_col=0)
sentiment_scores = pd.read_csv('sentiment_scores.csv', index_col=0)

demography_data = demography_data.sort_values(by='Abbreviation').reset_index(drop=True)
sentiment_scores = sentiment_scores.sort_values(by='Abbreviation').reset_index(drop=True)

app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#f5f5f5'},  # Common background color
                      children=[
    html.H1('State wise correlation between various national topics and their respective sentiment scores', style={'textAlign': 'center', 'color': '#333'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='demographic-dropdown',
                options=[{'label': col, 'value': col} for col in demography_data.columns if col not in ['State', 'Abbreviation', 'FIPS Code']],
                value='income'
            ),
        ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            dcc.Dropdown(
                id='topic-dropdown',
                options=[{'label': col, 'value': col} for col in sentiment_scores.columns if col not in ['state', 'Abbreviation']],
                value='abortion_sentiment'
            ),
        ], style={'width': '45%', 'float': 'right', 'display': 'inline-block', 'padding': '10px'}),
    ]),
    html.Div([
        dcc.Graph(id='demographic-map', style={'height': '50vh'}),
    ], style={'width': '45%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='sentiment-map', style={'height': '50vh'}),
    ], style={'width': '50%', 'float': 'right', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='scatter-plot', style={'height': '60vh'}),
    ], style={'width': '90%', 'display': 'block', 'marginLeft': 'auto', 'marginRight': 'auto', 'padding': '10px 20px'}),

])

@app.callback(
    Output('demographic-map', 'figure'),
    Input('demographic-dropdown', 'value')
)
def update_demographic_map(selected_demographic):
    fig = px.choropleth(
        demography_data,
        locations='Abbreviation',
        locationmode="USA-states",
        color=selected_demographic,
        scope="usa",
        color_continuous_scale='Blues'
    )
    return fig

@app.callback(
    Output('sentiment-map', 'figure'),
    Input('topic-dropdown', 'value')
)
def update_sentiment_map(selected_topic):
    fig = px.choropleth(
        sentiment_scores,
        locations='Abbreviation',
        locationmode="USA-states",
        color=selected_topic,
        scope="usa",
        color_continuous_scale='RdBu',
        range_color=[-1, 1]
    )
    return fig

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('demographic-dropdown', 'value'),
     Input('topic-dropdown', 'value')]
)
def update_scatter_plot(selected_demographic, selected_topic):
    X = demography_data[selected_demographic].values.reshape(-1, 1)
    y = sentiment_scores[selected_topic].values

    reg = LinearRegression().fit(X, y)

    min_x, max_x = X.min(), X.max()
    line_X = [[x] for x in range(int(min_x), int(max_x)+1)]

    line_y = reg.predict(line_X)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[x[0] for x in X], y=y, mode='markers', name='Data'))
    fig.add_trace(go.Scatter(x=[x[0] for x in line_X], y=line_y, mode='lines', name='Regression Line'))

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
