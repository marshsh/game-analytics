import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib

from plotly_calplot import calplot
import json

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Users and Revenue Simulator"

server = app.server
app.config.suppress_callback_exceptions = True




def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Game Profitability Analytics"),
            html.H3("Welcome to the Users and Revenue Simulator Dashboard"),
            html.Div(
                id="intro",
                children="Explore how different characteristics on how well the game is adopted by the public and how much revenue each user aports impacts the game's profitability.",
            ),
        ],
    )

# **** Div

def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card-2",
        children=[
            html.P("Select Time Frame to be shown on graphs"),
            dcc.DatePickerRange(
                id="time-frame-select",
                start_date=dt(2023, 1, 1),
                end_date=dt(2025, 12, 31),
                min_date_allowed=dt(1950, 1, 1),
                max_date_allowed=dt(2050, 12, 31),
                initial_visible_month=dt(2023, 6, 20),
            ),

            html.Br(),
            html.Br(),
            html.P("Initial user count"),
            dcc.Input(id="inicial-user-count", value=100.0, type="number", min=0, placeholder="Starting user count"),

            html.Br(),
            html.Br(),
            html.P("User Acquisition Cost"),
            dcc.Input(id="user-acq-cost", value=1.0, type="number", min=0),

            html.Br(),
            html.Br(),
            html.P("Budget per Month"),
            html.Div(children="Total user acquisition budget per month in USD."),
            dcc.Input(id="budget-per-month", value=100.0, type="number", min=0),

            html.Br(),
            html.Br(),
            html.P("Organic Spinoff"),
            html.Div(children="Percentage of new users for each user acquired. For example, people inviting new friends to the game."),
            dcc.Input(id="organic-spinoff", value=0.0, type="number", min=0),

            html.Br(),
            html.Br(),
            html.P( html.Big( "Decay Rate")),
            html.Div(children="Percentage of users that leave the game after the first day, first week, first month ..."),
            
            html.Br(),
            html.P("Decay rate for first day"),
            dcc.Input(id="decay-first-day", value=0.111, type="number", min=0.0000001, placeholder="Decay rate for first day"),

            html.Br(),
            html.Br(),
            html.P("Decay rate for first week"),
            dcc.Input(id="decay-first-week", value=0.11, type="number", min=0.0000001, placeholder="Decay rate for first week"),

            html.Br(),
            html.Br(),
            html.P("Decay rate for first month"),
            dcc.Input(id="decay-first-month", value=0.1, type="number", min=0.0000001, placeholder="Decay rate for first month", step=0.1),

            html.Br(),
            html.Br(),
            html.P("ARPDAU: Average Revenue per daily active user"),
            dcc.Input(id="arpdau", value=0.0, type="number", min=0, placeholder="ARPDAU"),

            html.Br(),
            html.Br(),
            html.P("Add events that will add users recurrently"),
                      
            html.Br(),
            html.Br(),
        ],
    )


app.layout = html.Div(
    id="app-container",
    children=[
        # DataFrames
        # dcc.Store(id='memory-output'),
        dcc.Store(id="new_users"),
        dcc.Store(id='users_per_day' ),
        # dcc.Store(id='df_revenue_per_day' ),


        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("plotly_logo.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(),  generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # Revenue per day Heatmap
                html.Div(
                    id="revenue_day_heatmap_card",
                    children=[
                        html.B("Revenue per day Heatmap NOW"),
                        html.Hr(),
                        dcc.Graph(id="revenue_day_heatmap"),
                    ],
                ),
                # Number of users per day Heatmap
                html.Div(
                    id="user_count_heatmap_card",
                    children=[
                        html.B("Number of users per day Heatmap"),
                        html.Hr(),
                        dcc.Graph(id="user_count_heatmap"),
                    ],
                ),
            ],
        ),
    ],
)



# **** UPDATE

# @app.callback(
#     [
#         Output("revenue_day_heatmap", "figure"),
#         Output("user_count_heatmap", "figure"),
#     ],
#     [
#         Input("time-frame-select", "start_date"),
#         Input("time-frame-select", "end_date"),
#         Input("user-acq-cost", "value"),
#         Input("budget-per-month", "value"),
#         Input("organic-spinoff", "value"),
#         Input("decay-first-day", "value"),
#         Input("decay-first-week", "value"),
#         Input("decay-first-month", "value"),
#         Input("arpdau", "value"),
#         Input("inicial-user-count", "value"),
#     ],
# )
# def update_info(start_date, end_date, user_acq_cost, budget_per_month, spinoff, decay_first_day, decay_first_week, decay_first_month, arpdau, user_count_init, user_count_date):
#     """Params:

#     'time-frame-select.start_date'
#     'time-frame-select.end_date'
#     'user-acq-cost'
#     'budget-per-month'
#     'organic-spinoff'
#     'decay-first-day'
#     'decay-first-week'
#     'decay-first-month'
#     'arpdau'
#     'inicial-user-count'
#     """
#     # Find which one has been triggered
#     ctx = dash.callback_context


#     bool_update_new_users = False
#     bool_update_users_count = False

#     if ctx.triggered:

#         for changed_prop in ctx.triggered[0]["prop_id"].split("."):

#             if changed_prop in ["time-frame-select", "decay-first-day", "decay-first-week", "decay-first-month", "inicial-user-count"]:
#                 bool_update_new_users = True
#                 bool_update_users_count = True
#             if changed_prop in ["time-frame-select", "decay-first-day", "decay-first-week", "decay-first-month", "inicial-user-count"]:
#                 bool_update_users_count = True
                
#             # elif changed_prop == "user-acq-cost":
#             # elif changed_prop == "budget-per-month":
#             # elif changed_prop == "organic-spinoff":
#             # elif changed_prop == "decay-first-day":
#             # elif changed_prop == "decay-first-week":
#             # elif changed_prop == "decay-first-month":
#             # elif changed_prop == "arpdau":
#             # elif changed_prop == "inicial-user-count":
#                 a = 42

#         prop_id = ctx.triggered[0]["prop_id"].split(".")[0]


#     if update_users_per_day:
#         update_new_users(start_date, end_date, spinoff, user_count_init)
#     if bool_update_users_count:
#         update_users_count(decay_first_day, decay_first_week, decay_first_month)

    

#     return revenue_heatmap(), user_count_heatmap()



@app.callback(
    Output("new_users", 'data'),
    [
        Input("time-frame-select", "start_date"),
        Input("time-frame-select", "end_date"),
        Input("organic-spinoff", "value"),
        Input("inicial-user-count", "value"),
        Input("user-acq-cost", "value"),
        Input("budget-per-month", "value"),
    ],
)
def update_new_users(start_date, end_date, spinoff, user_count_init, user_aqu_cost, budget_per_month):
    df_new_users = pd.DataFrame({
        'date': pd.date_range(start_date, end_date),
        'val': np.zeros((pd.to_datetime(end_date) - pd.to_datetime(start_date)).days + 1)
    }).set_index('date')

    if df_new_users is None:
        raise PreventUpdate

    # Initial Users
    data = list(df_new_users['val'])
    data[0] = user_count_init

    # Acquired Users
    new_daily_users_acqu = budget_per_month/user_aqu_cost
    data = [x + new_daily_users_acqu for x in data ]


    # Apply spinoff
    data = data*(spinoff + 1)

    return [ json.dumps(data) ]

    # return df_new_users.to_dict('records')
    # return {'data':list(df_new_users['val'])}

# NOW df[pd.to_datetime("2023-1-20")<df.ds][df.ds<pd.to_datetime("2023-1-30")]

@app.callback(
        Output("users_per_day", "data"),
    [
        Input("decay-first-day", "value"),
        Input("decay-first-week", "value"),
        Input("decay-first-month", "value"),
        Input("inicial-user-count", "value"),
        Input("new_users", 'data'),
    ],
)
def update_users_count(decay_first_day, decay_first_week, decay_first_month, initial_user_count, new_users_data):
    # Getting the new users
    new_users = json.loads(new_users_data[0])
    # if new_users is None:
    #     print( " ***** /n/n/n/n/n/n/n/n {}  /n/n/n/n/n/n/n/n   ***** ".format(new_users) )
    #     raise Exception("Sorry, no need to updte.")

    # print(" ***** /n/n/n/n/n/n/n/n {}   /n/n/n/n/n/n/n/n  {} ***** ".format(new_users, len(new_users)))


    # Users after first day of decay (We use the proportion inputed by user)
    users_day_two = np.roll(new_users,1)*decay_first_day
    users_day_two[0] = 0

    # print(" ***** /n/n/n/n/n/n/n/n {}   /n/n/n/n/n/n/n/n  {} ***** ".format(users_day_two, len(users_day_two)))

    # Parameters of the exponential decay deduced from the decay proportions on the 
    # first week and month:
    # 
    # If we asume an exponential decay of the form:
    #     a*exp(-lambda*time) = N(time) = percentage of initial population
    # and we have the proportion of the population left at time 7 and 30,
    # doing some algebra we can get the values of a and lambda to get the

    a =  decay_first_week**(30/23) * initial_user_count * decay_first_month**(-7/23)
    lam = -np.log(decay_first_week**(-7/23) * decay_first_month**(7/23))/7

    # Cumulative sum of users with decay on day 2 and forward
    users_per_day = np.zeros(len(users_day_two))
    for i, day_2_users in enumerate(users_day_two):
        if i == 0:
            continue
        users_per_day[i] = day_2_users + users_per_day[i-1]*np.exp(- decay_first_month)

    # Total cumulative sum
    users_per_day += new_users

    # df_users_per_day = pd.DataFrame({
    #     'date': pd.date_range(start_date, end_date),
    #     'val': users_per_day
    # }).set_index('date')


    # data = list(df_new_users['val'])
    # data[0] = user_count_init*spinoff

    return [ json.dumps(list(users_per_day)) ]



    # return {"data": users_per_day}




@app.callback(
        Output("revenue_day_heatmap", "figure"),
    [
        Input("users_per_day", "data"),
        Input("time-frame-select", "start_date"),
        Input("time-frame-select", "end_date"),
    ],
)
def revenue_heatmap(users_per_day_data, start_date, end_date):
    users_per_day = json.loads(users_per_day_data[0])



    df_users_per_day = pd.DataFrame({
        'date': pd.date_range(start_date, end_date),
        'val': users_per_day
    })

    fig = calplot(
        df_users_per_day,
        x="date",
        y="val",
        dark_theme=True,
        years_title=True,
        colorscale="purples",
        gap=0,
        name="Data",
        month_lines_width=3, 
        month_lines_color="#fff",
    )

    for i, data_i in enumerate(fig.data):
        hovertemplate_i = "<b> %{y}  %{x} <br><br> %{z} USD"
        data_i['hovertemplate']=hovertemplate_i

    return {"data": fig.data, "layout": fig.layout}



@app.callback(
        Output("user_count_heatmap", "figure"),
    [
        Input("users_per_day", "data"),
        Input("time-frame-select", "start_date"),
        Input("time-frame-select", "end_date"),
    ],
)
def user_count_heatmap(users_per_day_data, start_date, end_date):
    # end_date_2 = dt(start_date) + datetime.timedelta(days = len(users_per_day))

    users_per_day = json.loads(users_per_day_data[0])

    # print(" ***** /n /n /n /n /n /n /n /n {}   /n/n/n/n/n/n/n/n  {} ***** ".format(users_per_day, len(users_per_day)))


    df_users_per_day = pd.DataFrame({
        'date': pd.date_range(start_date, end_date),
        'val': users_per_day
    })

    print(" ***** /n /n /n /n /n /n /n /n {}   /n/n/n/n/n/n/n/n  {} ***** ".format(df_users_per_day, len(df_users_per_day)))


    fig = calplot(
        df_users_per_day,
        x="date",
        y="val",
        dark_theme=True,
        years_title=True,
        colorscale="purples",
        gap=0,
        name="Data",
        month_lines_width=3, 
        month_lines_color="#fff"
    )

    for i, data_i in enumerate(fig.data):
        hovertemplate_i = "<b> %{y}  %{x} <br><br> %{z} users"
        data_i['hovertemplate']=hovertemplate_i



    return {"data": fig.data, "layout": fig.layout}




# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
