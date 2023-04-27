import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server
# -- Import and clean data (importing csv into pandas)
# df = pd.read_csv("intro_bees.csv")
df = pd.read_csv('final_data.csv')
bp_df = df.drop(['PREDICTED_SBP', 'PREDICTED_DBP'], axis=1)
sd_bp_df = pd.DataFrame()
for cols in bp_df:
  #print(cols)
  if cols not in ['MSR_ID', 'CYC_ID','SBP', 'DBP']:
    sd_bp_df[cols] = bp_df.groupby('MSR_ID')[cols].std().reset_index()[cols]

f_columns = [col for col in sd_bp_df]

table_df1 = pd.read_csv('correlations.csv')

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("FEATURE ANALYTICS DASHBOARD", style={'text-align': 'center'}),

    # dcc.Dropdown(id="slct_year",
    #              options = f_columns,
    #              multi=False,
    #              value='PTT_PPG_DIASTOLIC',
    #              style={'width': "40%", 'color': 'hotpink', 'font-size': 12},
    #              clearable=False
    #              ),

    # html.Div(id='output_container', children=[]),
    # html.Br(),
    html.Br(),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H6('SELECT FEATURE :', className='navbar-text navbar-light bg-light text-right'), width=2),
            dbc.Col([dcc.Dropdown(id="slct_year",
                 options = f_columns,
                 multi=False,
                 value='PTT_PPG_DIASTOLIC',
                 style={'width': "50%",  'font-size': 14},
                 clearable=False
                 ),
                #  html.Div(id='output_container', children=[], className='navbar-text'),
                 html.Br()])
        ], className="g-1"),
        dbc.Row([
            dbc.Col(html.Div(id='plot1', children=[
             dcc.Graph(id='sd_plot', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
         ])),
            dbc.Col(html.Div(id='plot1', children=[
             dcc.Graph(id='df_plot', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
         ]))
        ]),

        dbc.Row([
            dbc.Col(html.Div(id='plot2', children=[
             dcc.Graph(id='scatter_sys', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
         ])),
            dbc.Col(html.Div(id='plot3', children=[
             dcc.Graph(id='scatter_dia', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
         ]))
        ]),
        dbc.Row([
            html.Br(),
            html.H5('PEARSON AND MIC VALUES', className='text-center navbar-text navbar-light bg-light')]
        ),
        dbc.Row([
            dbc.Col(dash_table.DataTable(
                data=table_df1.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in table_df1.columns],
                sort_action='native',
                css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                style_cell={
                    'width': '{}%'.format(len(table_df1.columns)),
                    'textOverflow': 'ellipsis',
                    'overflow': 'hidden'
    }
                ))
        ]),
        html.Br(),
        
    ]),

    # html.Div(id='plots', children=[
    #     html.Div(id='plot1', children=[
    #         dcc.Graph(id='sd_plot', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
    #     ]),
    #     html.Div(id='plot2', children=[
    #         dcc.Graph(id='scatter_sys', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
    #     ]),
    #     html.Div(id='plot3', children=[
    #         dcc.Graph(id='scatter_dia', figure={}, style={'display': 'flex'}, config={'modeBarButtonsToRemove': ['select2d', 'lasso2d'], 'displaylogo': False})
    #     ])
    # ], style={'display': 'flex','flex-wrap': 'wrap', 'justify-content': 'center',  'width': '80vw', 'height': '100vh'})
    
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [#Output(component_id='output_container', component_property='children'),
     Output(component_id='sd_plot', component_property='figure'),
     Output(component_id='df_plot', component_property='figure'),
     Output(component_id='scatter_sys', component_property='figure'),
     Output(component_id='scatter_dia', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))

    container = "FEATURE SELECTED: {}".format(option_slctd)

    # sd_dff = sd_bp_df.copy()
    # bp_dff = bp_df.copy()
    # dff = dff[dff["Year"] == option_slctd]
    # dff = dff[dff["Affected by"] == "Varroa_mites"]

    # Plotly Express
    fig1 = px.histogram(sd_bp_df, x=option_slctd, nbins=50, color_discrete_sequence = ['hotpink'])
    fig1.update_traces(marker_line_width=1,marker_line_color="white")
    fig1.update_layout(
    title={
        'text': "Distribution of Standard Deviation",
        'y':0.93,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig1_1 = px.histogram(bp_df, x=option_slctd, nbins=50, color_discrete_sequence = ['hotpink'])
    fig1_1.update_layout(
    title={
        'text': "Distribution of Feature Values",
        'y':0.93,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig1_1.update_traces(marker_line_width=1,marker_line_color="white")
    fig2 = px.scatter(bp_df, x=option_slctd, y='DBP', color_discrete_sequence = ['hotpink'])
    fig2.update_layout(
    title={
        'text': "DBP vs Selected Feature",
        'y':0.93,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig3 = px.scatter(bp_df, x=option_slctd, y='SBP', color_discrete_sequence = ['hotpink'])
    fig3.update_layout(
    title={
        'text': "SBP vs Selected Feature",
        'y':0.93,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
   

    return fig1,fig1_1,fig2, fig3


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)