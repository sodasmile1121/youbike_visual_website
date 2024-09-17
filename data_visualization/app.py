from dash import Dash, html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from styles import *

# 從queries.sql抓查詢
def read_sql_queries(file_path):
    queries = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        sections = content.split('--')
        for section in sections:
            lines = section.strip().split('\n', 1)
            if len(lines) < 2:
                continue
            query_name = lines[0].strip()
            query_text = lines[1].strip()
            queries[query_name] = query_text
    return queries

queries = read_sql_queries('queries.sql')

# 輸入查詢抓取對應資料
def get_data(string):
    conn = sqlite3.connect('../data_engineering/ubike.db')
    query = queries[string]
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 產生可複用組件
def gen_date_dropdown(idName):
    return dcc.Dropdown(
        id=idName,
        options=[
            {'label': 'Overall', 'value': 'all'},
            {'label': '2024-09-08', 'value': '2024-09-08'},
            {'label': '2024-09-09', 'value': '2024-09-09'},
            {'label': '2024-09-10', 'value': '2024-09-10'},
            {'label': '2024-09-11', 'value': '2024-09-11'},
            {'label': '2024-09-12', 'value': '2024-09-12'},
            {'label': '2024-09-13', 'value': '2024-09-13'},
            {'label': '2024-09-14', 'value': '2024-09-14'}
        ],
        value='all',
        style=drop_down_style
    )

def gen_reg_dropdown(idName):
    return dcc.Dropdown(
        id=idName,
        options=[{'label': 'Overall', 'value': 'all'}] + [{'label': region, 'value': region} for region in regions],
        value='all', 
        clearable=False,
        style=drop_down_style
    )

def gen_date_radio(idName):
    return dcc.RadioItems(
        id=idName,
        options=[
            {'label': '9/8', 'value': '2024-09-08'},
            {'label': '9/9', 'value': '2024-09-09'},
            {'label': '9/10', 'value': '2024-09-10'},
            {'label': '9/11', 'value': '2024-09-11'},
            {'label': '9/12', 'value': '2024-09-12'},
            {'label': '9/13', 'value': '2024-09-13'},
            {'label': '9/14', 'value': '2024-09-14'}
        ],
        value='2024-09-08',
        style={
            'display': 'flex',  
            'flexDirection': 'row', 
            'gap': '10px', 
        },
    )

def gen_col(string, item):
    return dbc.Col(
        html.Div([
            html.Div(string, style={'font-weight': 'bold'}),
            html.Div(f"{'{:,}'.format(item)}"),
        ], style=summary_style),
        width=3
    )

def gen_scatter_chart():
  return px.scatter(
        scatter_df,
        x='population_density',
        y='usage_ratio',
        labels={'population_density': 'Population Density (x1000)', 'usage_ratio': 'Usage Ratio (%)'},
        hover_name='sarea',
        text='sarea',
        title='Population Density vs. Usage Ratio by Region',
        template='plotly_dark'
    ).update_layout(
        xaxis_title='Population Density (x1000)',
        yaxis_title='',
        yaxis=dict(tickformat='.0%'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=320,
        width=700,
        title_x=0.06,
        margin=dict(l=80, r=0, t=40, b=20),
    ).update_traces(
        textposition='top center'
    )

def gen_bar_chart():
    return px.bar(
              cross_df,
              x='route_type',
              y='percentage',
              text='percentage',
              title='Percentage of Transactions by Route Type'
            ).update_layout(
              xaxis_title='',
              yaxis_title='',
              paper_bgcolor='rgba(0,0,0,0)', 
              plot_bgcolor='rgba(0,0,0,0)', 
              font=dict(color='white'),      
              xaxis=dict(showgrid=False),   
              yaxis=dict(
                  showgrid=False,          
                  tickformat='.0%',
                  range=[0, 1],
                  tickvals=[0.2, 0.4, 0.6, 0.8, 1.0], 
                  ticktext=['20%', '40%', '60%', '80%', '100%']  
              ),
              height=350,
              width=500,
              margin=dict(l=80, r=0, t=40, b=20),
            ).update_traces(
              texttemplate='%{text:.0%}', textposition='outside'
            ).update_xaxes(
              tickvals=['same_district', 'different_district'],
              ticktext=['same district', 'cross district']
            )

def gen_data_table(idName, columnList, df, style):
    return dash_table.DataTable(
        id=idName,
        columns=columnList,
        data=df.to_dict('records'),
        style_table=style,
        style_header=table_header_style,
        style_cell=table_cell_style,
        style_data=table_data_style,
        page_size=10
    )

def map_value_to_color(value, min_value, max_value):
    norm_value = (max_value - value) / (max_value - min_value)
    color = plt.cm.plasma(norm_value) 
    return f'rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})' 

# 事前準備所需資料
summary_df = get_data('summary')
regions = get_data('region')['sarea'].tolist()
scatter_df = get_data('scatter')
route_df = get_data('route')
cross_df = get_data('cross')
visibility_df = get_data('visibility')
sna_df = get_data('sna')
org_des_df = get_data('orgdes')
txt_sum_min = route_df['sum_of_txn_times'].min()
txt_sum_max = route_df['sum_of_txn_times'].max()

routes = []
for _, row in route_df.iterrows():
    color = map_value_to_color(row['sum_of_txn_times'], txt_sum_min, txt_sum_max)
    routes.append(go.Scattermapbox(
        mode="lines+markers+text",
        lon=[row['on_stop_lon'], row['off_stop_lon']],
        lat=[row['on_stop_lat'], row['off_stop_lat']],
        line=dict(width=5, color=color),
        text=[row['on_stop'], row['off_stop']],
        textposition="top right",
        marker=dict(size=8, color=color),
        name=f"{row['on_stop']} to {row['off_stop']}"
    ))

total = summary_df['total'][0]
rent = summary_df['rent'][0]
return_bike = summary_df['return'][0]
ratio = summary_df['ratio'][0]

# 主程式碼
app = Dash(external_stylesheets=[dbc.themes.CYBORG])

app.layout = html.Div([
    html.H3(
        children='Explore Data with Youbike 2.0',
        style=header_style
    ),

    html.Hr(),

    dbc.Row([
        gen_col(f"Total", total),
        gen_col(f"Rent", rent),
        gen_col(f"Return", return_bike),
        gen_col(f"Ratio", ratio),
    ]),

    dbc.Row([
        dbc.Col(
            html.Div([
                gen_date_dropdown('date-dropdown'),
                dcc.Graph(id='bubble-chart')
            ]), width=7
        ),
        dbc.Col(
            html.Div([
                gen_reg_dropdown('region-dropdown'),
                dcc.Graph(
                  id='daily-chart',
                ),
                html.Div([
                    html.Div([
                      gen_date_radio('date-selector'),
                    ], style=radio_place_style),
                    
                    dcc.Graph(
                        id='hourly-chart',
                    ),
                ]),  
            ]), width=5
        ),
    ]),
    
    dbc.Row([
        dbc.Col(
          dcc.Graph(
              id='scatter-plot',
              figure=gen_scatter_chart(),
          ), width=7
        ),
        dbc.Col(
          dcc.Graph(
            id='cross-plot',
            figure=gen_bar_chart(),
        ), width=5
      )
    ]),
    
    gen_reg_dropdown('area-dropdown'),
    
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='visibility_graph'), width=5
        ),
        dbc.Col(
            gen_data_table(
                'usage-table', 
                [
                  {'name': '區域', 'id': 'sarea'},
                  {'name': '站點名稱', 'id': 'sna'},
                  {'name': '使用率', 'id': 'usage_ratio'}
                ], 
                sna_df, 
                {
                  'width': '450px',  
                  'height': '400', 
                  'margin': '40px 0px 0px 300px' 
              }
            ), width=7
        )
    ]),
    
    dcc.Graph(
            id='map',
            figure={
                'data': routes,
                'layout': go.Layout(
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lat=route_df[['on_stop_lat', 'off_stop_lat']].mean().mean(), lon=route_df[['on_stop_lon', 'off_stop_lon']].mean().mean()),
                        zoom=10.5
                    ),
                    title={
                        'text': 'Top 15 Routes', 
                        'x': 0, 
                        'font': {
                            'color': 'white'  
                        }
                    },
                    legend=dict(
                        font=dict(color='white')  
                    ),
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',  
                    margin=dict(l=0, r=0, t=40, b=0)
                )
            },
            style=route_style
    ), 
      
    html.Div(
      gen_data_table(
          'transaction-table', 
          [
            {'name': '起點區', 'id': 'district_origin'},
            {'name': '起點站', 'id': 'on_stop'},
            {'name': '終點區', 'id': 'district_destination'},
            {'name': '終點站', 'id': 'off_stop'},
            {'name': '消費次數', 'id': 'total_txn_times'}
          ],
          org_des_df, 
            {
              'overflowX': 'auto',
              'height': '400px',
              'width': '1300px',
            }
          ),
        style=large_table_style
    ),

])

# Callback Function
@app.callback(
    Output('bubble-chart', 'figure'),
    [Input('date-dropdown', 'value')]
)

def update_bubble_chart(selected_date):
    conn = sqlite3.connect('../data_engineering/ubike.db')
    if selected_date == 'all':
        query = queries['overallUsage']
        
    else:
        query = queries['specificUsage'].format(selected_date=selected_date)
    df = pd.read_sql_query(query, conn)
    conn.close()

    fig = px.scatter_mapbox(
        df,
        title='Usage Ratio By District',
        lat='latitude',
        lon='longitude',
        size=df['usage_ratio'], 
        color='sarea', 
        hover_name='sarea', 
        size_max=30,  
        zoom=10.5, 
        center=dict(lat=25.0330, lon=121.5654),
        mapbox_style="open-street-map",  
        height=600,
        width=800
    )

    fig.update_layout(
        margin=dict(l=40, r=0, t=40, b=0),  
        paper_bgcolor='rgba(0,0,0,0)',   
        plot_bgcolor='rgba(0,0,0,0)',    
        title_font_color='white'
    )
    return fig

@app.callback(
    Output('daily-chart', 'figure'),
    [Input('region-dropdown', 'value')]
)

def update_daily_chart(selected_region):
    conn = sqlite3.connect('../data_engineering/ubike.db')

    if selected_region == 'all':
      query = queries['overallDailyUsage']
    else:
      query = queries['specificRegionDailyUsage'].format(selected_region=selected_region)
    
    day_df = pd.read_sql_query(query, conn)
    conn.close() 
    
    fig = px.line(
        day_df,
        x='mday',
        y='usage_ratio',
        labels={'mday': 'Date', 'usage_ratio': 'Usage Ratio'},
        title=f'Usage Ratio Over Time ({selected_region if selected_region != "all" else "Overall"})',
        height=300,
        width=500,
        line_shape='linear'
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='', 
        xaxis=dict(
            tickformat='%m/%d',  
            showgrid=False,      
            tickfont=dict(color='white'),
        ),
        yaxis=dict(
            showgrid=False,     
            tickfont=dict(color='white'),  
            range=[0.4, 1],
            tickvals=[0.5, 0.6, 0.7, 0.8, 0.9], 
            ticktext=['50%', '60%', '70%', '80%', '90%'] 
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=20, r=20, t=30, b=20),  
        title_font_color='white',  
    )

    fig.update_traces(
        line=dict(color='white')  
    )

    return fig

@app.callback(
    Output('hourly-chart', 'figure'),
    [Input('region-dropdown', 'value'),
     Input('date-selector', 'value')]
)

def update_hourly_graph(selected_region, selected_date):
    conn = sqlite3.connect('../data_engineering/ubike.db')

    if selected_region == 'all':
        query = queries['overallHourlyUsage'].format(selected_date=selected_date)

    else:
        print(selected_region)
        query = queries['specificDateHourlyUsage'].format(selected_region=selected_region, selected_date=selected_date)
        print(query)
    
    hour_df = pd.read_sql_query(query, conn)
    conn.close() 
    
    fig = px.line(
        hour_df,
        x='infoHour',
        y='usage_ratio',
        labels={'infoHour': 'Hour of Day', 'usage_ratio': 'Usage Ratio'},
        title=f'Usage Ratio by Hour ({selected_region if selected_region != "all" else "Overall"})',
        height=300,
        width=500,
        line_shape='linear'
    )

    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        xaxis=dict(
            tickformat='%H:%M',  
            showgrid=False,      
            tickfont=dict(color='white'),
        ),
        yaxis=dict(
            showgrid=False,     
            tickfont=dict(color='white'),
            range=[0.3, 1],
            tickvals=[0.4, 0.5, 0.6, 0.7, 0.8, 0.9], 
            ticktext=['40%', '50%', '60%', '70%', '80%', '90%']  
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)', 
        margin=dict(l=20, r=20, t=30, b=20),  
        title_font_color='white',  
    )

    fig.update_traces(
        line=dict(color='white')  
    )

    return fig


@app.callback(
    Output('visibility_graph', 'figure'),
    Input('area-dropdown', 'value')
)
def update_graph(selected_area):
    if selected_area == 'all':
        filtered_df = visibility_df
    else:
        filtered_df = visibility_df[visibility_df['sarea'] == selected_area]

    fig = px.scatter(
        filtered_df,
        x='category',
        y='capacity',
        color='sarea',
        labels={'category': '見車率', 'capacity': '車輛總數'},
        title='Capability vs. Visibility by Station',
        hover_name='stop_name',
        category_orders={'category': ['低', '中', '高']},
        template='plotly_dark'
    ).update_layout(
        xaxis_title='Visibility',
        yaxis_title='Capability',
        plot_bgcolor='rgba(0,0,0,0)',  
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='white'),        
        height=400,
        width=700,
        margin=dict(l=80, r=0, t=40, b=20),
    ).update_traces(
        textposition='top center'
    )

    return fig

@app.callback(
    Output('usage-table', 'data'),
    Input('area-dropdown', 'value')
)
def update_table(selected_region):
    if selected_region == 'all':
        filtered_df = sna_df
    else:
        filtered_df = sna_df[sna_df['sarea'] == selected_region]
    
    return filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)
