import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
from dash import Dash, dcc, html, Input, Output, dash_table,callback  # pip install dash (version 2.0.0 or higher)
import dash_bootstrap_components as dbc
import numpy as np
from helpers.utilx import get_user_metrics as gum
from helpers.utilx import normalise_radar_user as nru
import plotly.graph_objects as go

app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO],  meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server
px.set_mapbox_access_token(open(".mapbox_token").read())
#---------------------------------------------------------------
#DF DATA LOAD SECTION

users_all = [x for x in range(1,101)]
meta_df = pd.read_csv('data/noisemeta.csv')
peakmeta_df = pd.read_csv('data/block2/peakmeta.csv')
#-------------------------------------  --------------------------

#---------------------------------------------------------------
#COMPONENTS
header = html.H4(
    "Nsqrd Dashboard", className="bg-dark text-white p-2 mb-2 text-center"
    )
dropdown = html.Div(
    [
        dbc.Label("Select User:"),
                    dcc.Dropdown(
                        id="indicator",
                        options = users_all,
                        multi=False,
                        value=1,
                        clearable=False,
                        #className='mb-4'
                        className='text-black'
                    ),
    ],
    className="mb-4",
)
controls = dbc.Card(
    [
        dropdown, 
    ],
    body=True,
)
# tab1 = dbc.Tab([dcc.Graph(id="chart-1")], label="Top Interactions", style={'padding':'15px'})
tab1 = dbc.Tab([
    dbc.Row([ dcc.Graph(id="ecg") ]),
    dbc.Row([ dcc.Graph(id="ecg_filter") ]),
    dbc.Row([ dcc.Graph(id="ppg") ]),
    dbc.Row([ dcc.Graph(id="ppg_filter") ]),  
    ], label="Noise Filtering", style={'padding':'15px'})
tab2 = dbc.Tab([
    dbc.Row([ dcc.Graph(id="ecg_peak") ]),
    dbc.Row([ dcc.Graph(id="ppg_peak") ]),
    dbc.Row([ dbc.Row([], ) ], id='df_rowdata', style={'margin':'5px'}),

    ], label="Peak Detection", style={'padding':'15px'})
tab3 = dbc.Tab([
    dbc.Row([dbc.RadioItems(
            options=[
                {"label": "hourly", "value": 1},
                {"label": "daily", "value": 2},
                {"label": "weekly", "value": 3},
            ],
            value=1,
            id="temporal_inp",
            inline=True,
        ),]),
    dcc.Graph(id='chart-3')], label='Features', style={'padding':'15px'})
#tab3 = dbc.Tab([table], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

leftCard = dbc.Row([
    dbc.Row([ 
        html.H6("SIGNAL QUALITY", className="card-subtitle"),
        dcc.Graph(id="sigqual_fig", ), ],style={ 'height':100, 'width':'fit-content'}),
    dbc.Row([ 
        html.H6("ECG WANDER", className="card-subtitle"),
        dcc.Graph(id="ecg_wfig", ), ],style={ 'height':100, 'width':'fit-content'}),
    
    dbc.Row([ 
        html.H6("ECG NOISE", className="card-subtitle"),
        dcc.Graph(id="ecg_nfig", ), ],style={ 'height':100, 'width':'fit-content'}),
    dbc.Row([ 
        html.H6("PPG WANDER", className="card-subtitle"),
        dcc.Graph(id="ppg_wfig", ), ],style={ 'height':100, 'width':'fit-content'}),
    dbc.Row([ 
        html.H6("PPG NOISE", className="card-subtitle"),
        dcc.Graph(id="ppg_nfig", ), ],style={ 'height':100, 'width':'fit-content'}),
    
], style={'padding-top':5})

# leftCard = dcc.Graph(id="ecg_wfig", )

#---------------------------------------------------------------
#helper functions
def get_metavals(user):
    ewander = meta_df[meta_df['USER_ID']==user]['ECG_WANDER'].item()
    enoise = meta_df[meta_df['USER_ID']==user]['ECG_NOISE'].item()
    pwander = meta_df[meta_df['USER_ID']==user]['PPG_WANDER'].item()
    pnoise = meta_df[meta_df['USER_ID']==user]['PPG_NOISE'].item()
    # print(ewander, enoise, pwander, pnoise)
    return ewander, enoise, pwander, pnoise

def get_peakmetavals(user):
    ecghr = peakmeta_df[peakmeta_df['USER_ID']==user]['ECG_HR'].item()
    ppgfhr = peakmeta_df[peakmeta_df['USER_ID']==user]['PPG_F_HR'].item()
    ppgshr = peakmeta_df[peakmeta_df['USER_ID']==user]['PPG_S_HR'].item()
    ecgcyc = peakmeta_df[peakmeta_df['USER_ID']==user]['ECG_USE_CYC'].item()
    ppgcyc = peakmeta_df[peakmeta_df['USER_ID']==user]['PPG_USE_CYC'].item()
    totcyc = peakmeta_df[peakmeta_df['USER_ID']==user]['TOT_USE_CYC'].item()
    sigqual = peakmeta_df[peakmeta_df['USER_ID']==user]['SIGNAL_QLTY'].item()

    return ecghr, ppgfhr, ppgshr, ecgcyc, ppgcyc, totcyc, sigqual

def get_colorvals(val, sig= False, neutral=False):

    if neutral:
        return 'black'
    
    if not sig:    
        if val<0.34:
            bcolor='green'
        elif val < 0.67:
            bcolor='yellow'
        else:
            bcolor ='red'
    else:
        if val<34:
            bcolor='red'
        elif val < 67:
            bcolor='yellow'
        else:
            bcolor ='green'
    
    return bcolor

def get_indicatorGraph(val, sig=False, neutral=False):
    bcolor = get_colorvals(val,sig,neutral)
    gaugemax = 1
    if sig:
        gaugemax=100
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = val,
        title = {'text': ""},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {'shape': 'bullet',
                'axis': {'range':[0,gaugemax]},
                'bar': {'color': bcolor, 'thickness':0.7}
            },

    ))
    fig.update_layout(margin=dict(l=5, r=5, t=5, b=25), autosize=True, )
    return fig

#---------------------------------------------------------------
#APP LAYOUT SECTION
app.layout = dbc.Container(
    [
        header,
        # dbc.Row([ controls ]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        controls,
                        leftCard,                  
                    ],
                    width=3,
                ),
                dbc.Col(
                [
                    tabs,
                ], width=9),
            ]
        ),
    ],
    fluid=True,
    className="dbc",
)
#---------------------------------------------------------------

#---------------------------------------------------------------

#---------------------------------------------------------------

#---------------------------------------------------------------
#CALLBACK SECTION - THE BINDER
@callback(
    Output("ecg", "figure"),
    Output("ecg_filter", "figure"),
    Output("ppg", "figure"),
    Output("ppg_filter", "figure"),
    Output("ecg_wfig", "figure"),
    Output("ecg_nfig", "figure"),
    Output("ppg_wfig", "figure"),
    Output("ppg_nfig", "figure"),
    Output("ecg_peak", "figure"),
    Output("ppg_peak", "figure"),
    Output("sigqual_fig", "figure"),
    Output("df_rowdata", "children"),

    Input("indicator", "value"),
)
def update_page(indicator):
    userx = indicator  
    loc = 'data/USER_'+str(userx)+'.csv'
    peak_loc = 'data/block2/USER_'+str(userx)+'.csv'
    user = 'USER_'+str(userx)
    df = pd.read_csv(loc)
    peak_df = pd.read_csv(peak_loc)
    ecg_wander, ecg_noise, ppg_wander, ppg_noise = get_metavals(user)
    ecghr, ppgfhr, ppgshr, ecgcyc, ppgcyc, totcyc, sigqual = get_peakmetavals(user)
    ecgw_color = get_colorvals(ecg_wander)
    ecgn_color = get_colorvals(ecg_noise)
    ppgw_color = get_colorvals(ppg_wander)
    ppgn_color = get_colorvals(ppg_noise)

    sigqual_fig = get_indicatorGraph(sigqual,sig=True)

    ecg = px.line(df['ECG'], height=300, color_discrete_sequence = ['royalblue']) 
    ecg.update_layout(title=dict(text="RAW ECG",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')


    
    ecg_filter = px.line(df['filteredecg'], height=300, color_discrete_sequence = ['royalblue']) 
    ecg_filter.update_layout(title=dict(text="FILTERED ECG",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')
    
    ppg = px.line(df['PPG'], height=300, color_discrete_sequence = ['royalblue']) 
    ppg.update_layout(title=dict(text="RAW PPG",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')
    
    ppg_filter = px.line(df['filteredppg'], height=300, color_discrete_sequence = ['royalblue']) 
    ppg_filter.update_layout(title=dict(text="FILTERED PPG",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')
    
    ecg_wfig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ecg_wander,
        title = {'text': ""},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {'shape': 'bullet',
                'axis': {'range':[0,1]},
                'bar': {'color': ecgw_color, 'thickness':0.7}
            },

    ))
    ecg_wfig.update_layout(margin=dict(l=5, r=5, t=5, b=25), autosize=True, )
    
    ecg_nfig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ecg_noise,
        title = {'text': ""},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {'shape': 'bullet',
                'axis': {'range':[0,1]},
                'bar': {'color': ecgn_color, 'thickness':0.7}
            },

    ))
    ecg_nfig.update_layout(margin=dict(l=5, r=5, t=5, b=25), autosize=True,)
    
    ppg_wfig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ppg_wander,
        title = {'text': ""},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {'shape': 'bullet',
                'axis': {'range':[0,1]},
                'bar': {'color': ppgw_color, 'thickness':0.7}
            },

    ))
    ppg_wfig.update_layout(margin=dict(l=5, r=5, t=5, b=25), autosize=True,)
    
    ppg_nfig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = ppg_noise,
        title = {'text': ""},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge= {'shape': 'bullet',
                'axis': {'range':[0,1]},
                'bar': {'color': ppgn_color, 'thickness':0.7}
            },

    ))
    ppg_nfig.update_layout(margin=dict(l=5, r=5, t=5, b=25), autosize=True,)

    #SECOND TAB BEGINS
    ecg_peak = px.line(df['filteredecg'], height=300, color_discrete_sequence = ['royalblue']) 
    ecg_peak.update_layout(title=dict(text="ECG with peaks",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')
    ecg_peak.add_traces(
    go.Scatter(
       x=peak_df['ECG_R']-1,y=df['filteredecg'][peak_df['ECG_R']-1], mode="markers"
    )
    )
    
    ppg_peak = px.line(df['filteredppg'], height=300, color_discrete_sequence = ['royalblue']) 
    ppg_peak.update_layout(title=dict(text="PPG with peaks",),title_x=0.5,autosize=True, paper_bgcolor='whitesmoke',
                         xaxis=dict(rangeslider=dict(visible=True),
                             type="linear"), showlegend=False,xaxis_title='',yaxis_title='')
    ppg_peak.add_traces(
    go.Scatter(
       x=peak_df['PPG_F']-1,y=df['filteredppg'][peak_df['PPG_F']-1], mode="markers"
    )
    )
    ppg_peak.add_traces(
    go.Scatter(
       x=peak_df['PPG_S']-1,y=df['filteredppg'][peak_df['PPG_S']-1], mode="markers"
    )
    )

    df_rowdata = dbc.Table.from_dataframe(peakmeta_df[peakmeta_df['USER_ID']==user].iloc[:,4:-1], 
                                          striped=True, 
                                          bordered=True, hover=True,
                                          size='md',
                                          color='secondary')

    return ecg, ecg_filter, ppg, ppg_filter, ecg_wfig, ecg_nfig, ppg_wfig, ppg_nfig, ecg_peak, ppg_peak, sigqual_fig, df_rowdata
#---------------------------------------------------------------



if __name__ == '__main__':
    app.run_server(debug=True)