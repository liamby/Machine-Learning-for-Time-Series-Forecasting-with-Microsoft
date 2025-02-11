import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_table
import pandas as pd
from Log_Book_Class import Log_Book
from Log_Entry_Class import Log_Entry
from Log_Entry_Request_Class import Log_Entry_Request
from dash.dependencies import Output, Input, State

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.config['suppress_callback_exceptions'] = True

model_dict = {'Energy Data': ['Linear Regression', 'Support Vector Regression','Random Forest Regression'], 'Sunspots': ['SARIMAX', 'SARIMA']}
models = list(model_dict.keys())

log_entry_dict = {}
log_entries = []

################################################################################
############################### GLOBALS ########################################
################################################################################

# Colours that will be used throughout the UI
colors = {
    'main' : '#1a1c23',
    'log_book': '#22252b',
    'text': '#b2b2af',
    'graph':  '#21252c',
    'green': '#3d9970',
    'red': '#fc4136',
    'black': '#000000',
    'white' : '#FFFFFF',
    'header-color':'#2d332f',
    'bg-color':'#a1ada5'
}

styles = {
    'grey_text_on_black_background': {
        'color': colors['text'],
        'background-color': colors['main']
    }
}

dataset_choices = [
    'Energy Data',
    'Sunspots'
]

model_choices = [
    'Linear Regression',
    'Support Vector Regression',
    'Random Forest Regression',
    'SARIMAX',
    'SARIMA'
]


################################################################################
############################### FUNCTIONS ######################################
################################################################################


# Creates a log_book and fills it
def create_and_fill_log_book():
    log_book = create_log_book()
    return fill_log_book(log_book)


# This class will create log entries for the purpose of demonstration
def fill_log_book(log_book):
    log_book.append_log_entry(create_log_entry(Log_Entry_Request(dataset_choices[0], 'Linear Regression', 1/2)))
    log_book.append_log_entry(create_log_entry(Log_Entry_Request(dataset_choices[1], 'Linear Regression', 1/2)))
    log_book.append_log_entry(create_log_entry(Log_Entry_Request(dataset_choices[0], 'Linear Regression', 1/2)))
    log_book.append_log_entry(create_log_entry(Log_Entry_Request(dataset_choices[1], 'Linear Regression', 1/2)))
    return log_book


# This class will create log entrie for the purpose of demonstration
def create_log_book():
    log_book = Log_Book()
    return log_book


# Creates a log entry from a log_entry_request and returns it
def create_log_entry(log_entry_request):
    # If dropdown selected is a valid data
    if (log_entry_request.dataset in dataset_choices
        and log_entry_request.model in model_choices
            and log_entry_request.check_valid_ratio()):
        # Create a Log Entry
        log_entry = Log_Entry(log_entry_request.model,
                            log_entry_request.dataset,
                            time.asctime(time.localtime(time.time())),
                            log_entry_request.ratio)
        return log_entry
    else:
        print('log entry could not be created at create_log_entry(log_entry_request)', flush=True)


# Prints the logbook to the console
def print_log_book():
    print('LOGBOOK:')
    for i in range(len(log_book.log_entry_array)):
        print(log_book.log_entry_array[i].dataset, flush=True)


# Updates the logbook buttons being shown on the screen.
def update_log_book_buttons():
    return html.Div(
        children=[
            html.Tr(
                children=[
                    log_book.button_array[i]
                ]
            )
            for i in range(len(log_book.button_array))
        ]
    )

def change_right_hand_side(chosen):
    print('RHS changed to', flush=True)
    if chosen == 'log-entry':
        print('log entry', flush=True)
        return {'display': 'block'}, {'width': '100%', 'display': 'none', 'padding': '0 20'}
    elif chosen == 'log-entry-request':
        print('log entry request', flush=True)
        return {'display': 'none'}, {'width': '100%', 'display': 'block', 'padding': '0 20'}


def refresh_notes():
    return log_book.selected_log_entry.notes


################################################################################
############################### HTML LAYOUT ####################################
################################################################################


#Returns the HTML layout for the header
def header_layout():
    return html.Div(
        style={'width': '100%',
                'background-color': colors['header-color'],
                'color': colors['white']},
        children=[
            # Heading 1
            html.H1(children='Machine Learning Techniques for Time Series Forecasting',
                    style={
                            'display':'block',
                            'text-align':'center',
                            'font-size':35
                },
            ),
            # Heading 2
            html.H2(children='Microsoft Project Group 6',
                style={'text-align': 'center', 'font-size': 15
                },
            )
        ]
    )


# Returns the HTML Layout for logbook
def log_book_layout():
    return html.Div(
        children=[
            #html.H2(children='Logbook',
            #    style={
            #        'text-align': 'center',
            #        'font-size': 35,
            #        'color': colors['black'],
            #        'padding': 0
            #    }
            #),
            html.Div(
                style = {'text-align': 'center',
                        'display': 'block',
                        'margin-left': 'auto',
                        'margin-right': 'auto',
                        'margin-bottom': 'auto',
                        'width': '100%',
                        'background-color': colors['bg-color']},
                id='request_new_forecast_button',
                children=[log_book.request_new_forecast_button],
                n_clicks = 0
            ),
            html.Div(
                    dcc.Dropdown(
                        style={'font-family': 'sans-serif',
                                'text-align': 'center',
                                'display': 'block',
                                'margin-left': 'auto',
                                'margin-right': 'auto',
                                'width': '100%'
                                },
                        id='log-book-table',
                        options=[
                            {'label': key, 'value': key} for key in log_entry_dict
                        ],
                        placeholder='Select a Log Entry',
                        value = list(log_entry_dict.keys()),
                        clearable = False
                    ),
            )
        ]
    )


# Returns the HTML layout for log Entry
def log_entry_layout():
    # Update_log_entry_contents(log_book.selected_log_entry)
    return html.Div(
        id = 'log-entry',
        style={'width': '100%', 'height': '1000px', 'display': 'none','background-color':colors['bg-color']},
        children=[

            # Training Data Graph and div
            html.Div(style={'width': '50%','display': 'inline-block'},
                children=[
                    # Title
                    html.H3('Training Data Graph', style={'text-align': 'center'}),
                    # Graph
                    dcc.Loading(
                        children=[dcc.Graph(style={'width': '100%', 'height': '600px'},
                                            id='training-data-graph')],
                        type='circle',
                    ),
                ]
            ),

            # Forecasting Data Graph
            html.Div(style={'width': '50%', 'display': 'inline-block'},
                children=[
                    # Forecasting data graph
                    html.H3('Forecast Data Graph', style={'text-align': 'center'}),
                    dcc.Loading(
                        children=[
                            dcc.Graph(style={'width': '100%', 'height': '600px'},
                                        id='forecast-data-graph'),
                        ],
                        type='circle',
                    )
                ]
            ),

            html.Div(style={'display': 'block', 'margin-bottom':'20px'},
                children=[
                    # Forecasting data graph
                    html.H3('Notes', style={'text-align': 'center'}),
                    dcc.Loading(
                        children=[
                            html.Div(
                                style={'text-align': 'center', 'display' : 'grid'},
                                children = [
                                    dcc.Textarea(
                                        style={'width': '100%', 'height': 300, 'display': 'flex'},
                                        id='textarea',
                                        value = 'Please write your notes here',
                                    ),
                                    html.Button('Submit', id='textarea-button',style={'color':'#FFFFFF','background-color':'#2d332f'}, n_clicks=0),
                                ]
                            )
                        ],
                        type='circle',
                    )
                ]
            ),
        ]
    )


# Returns the HTML layout for the log entry request page
def log_entry_request_layout():
    return dcc.Loading(
        children = [
            html.Div(
                id = 'log-entry-request',
                style = {'display': 'block',
                         'color': colors['bg-color'],
                         'background-color':colors['bg-color'],
                         'width':'40%'},
                children=[
                    html.H3('Forecast Request Details',style={'text-align': 'center','background-color':colors['bg-color']}),
                    # Dataset dropdown + label div
                    html.Div(style={'text-align': 'center', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto','margin-bottom': '20px', 'width': '40%','background-color': colors['bg-color']},
                        children=[
                            html.Label(['Dataset']),
                            dcc.Dropdown(
                                id='Dataset-dropdown',
                                options=[
                                    {'label': model, 'value': model} for model in models
                                ],
                                placeholder='Select a Dataset',
                                #value=list(model_dict.keys())[0],
                            ),
                        ]
                    ),

                    # Model dropdown label + dropdown div
                    html.Div(style={'font-family': 'sans-serif', 'text-align': 'center', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'margin-bottom': '20px', 'width': '40%'},
                        children=[
                            # Label
                            html.Label(['Model']),
                            # Dropdown
                            dcc.Dropdown(
                                id='Model-dropdown',
                                placeholder='Select a Model',
                                value='None',
                            ),
                        ]
                    ),
                    html.Div(style={'font-family': 'sans-serif', 'text-align': 'center', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto', 'width': '40%'},
                    children=[
                        html.Label(['Percentage of the data to be used to train the model']),
                        html.Div(dcc.Input(id='input-box', type='text')),
                        dcc.Loading(
                            children=[
                                html.Button('Submit', id='submit-button',style={'color':colors['white'],'background-color':colors['header-color']}),
                                html.Div(id='output-container-button',
                                        children=['Enter a decimal (less than 1 but greater than 0) and press submit'])
                            ]
                        )
                        ]
                    )
                ]
            )
        ], type = 'circle'
    )


################################################################################
############################### APP LAYOUT #####################################
################################################################################

# Create log book
#log_book = create_and_fill_log_book()
log_book = create_log_book()

# Main layout for the app that calls all the other layout functions
app.layout = html.Div(
    style={'background-color': colors['bg-color'],
            'color': colors['black'],
            'width':'100%',
            'height':'1500px',
            'margin-left':0,
            'margin-right':0},
    children = [
        # Top Bar
        html.Div(
            id="top_bar",
            children=[header_layout()]
        ),
        # Log book
        html.Div(
            id="log_book", children=[log_book_layout()],
            style={
                'position': 'static',
                'width': '32%',
                'margin-left': 'auto',
                'margin-right': 'auto',
                'display': 'block',
                'background-color': colors['bg-color'],
                'margin-top': '50px',
                'margin-bottom': '20px'
                }
        ),
        # Left hand side of screen (either log entry request page or log entry page)
        html.Div(
            id="left-hand-side",
            children=[log_entry_request_layout(),
                      log_entry_layout()],
            style={
                'position': 'static',
                'width': '80%',
                'margin-left': 'auto',
                'margin-right': 'auto',
                'display': 'block',
                'background-color': colors['bg-color'],
                'margin-top': '50px',
                'margin-bottom': '200px'
                }
        ),
        html.Div(id='hidden-div', style={'display':'none'}),
        html.Div(id='hidden-div-2',style ={'display':'none'})
    ]
)


################################################################################
############################### CALLBACKS ######################################
################################################################################


# Called when option on log entry dropdown is selected
# Updates page to display information
@app.callback([Output('log-entry', 'style'),
                Output('log-entry-request', 'style'),
                Output('training-data-graph', 'figure'),
                Output('forecast-data-graph', 'figure'),
                Output('textarea', 'value')],
                [Input('log-book-table', 'value'),
                Input('request-new-forecast-button','n_clicks')],
                [State('textarea', 'value')]
                )
def update_display(entry,n_clicks,text):
    if entry == [] or n_clicks != 0:
       return ({'display': 'none'},
               {'width': '100%', 'display': 'block', 'padding': '0 20'},
               go.Figure(),
               go.Figure(),
               '')
    else:
        key = ''
        for i in log_entry_dict:
            if i == entry:
                key = i
                break
        return ({'display': 'block'},
                {'width': '100%', 'display': 'none', 'padding': '0 20'},
                log_entry_dict[key].training_graph,
                log_entry_dict[key].forecasting_graph,
                log_entry_dict[key].notes
                )


# Called when the submit button is pressed on the log entry request page.
# Creates a new log entry and stores it in the log entry dictionary
@app.callback([Output('request-new-forecast-button', 'n_clicks'),
             Output('log-book-table','options')],
            [Input('submit-button', 'n_clicks_timestamp')],
            [State('Dataset-dropdown', 'value'),
            State('Model-dropdown', 'value'),
            State('input-box', 'value')])
def submit_log_entry_request(button_value, dataset_dropdown_value,
                            model_dropdown_value, input_box_value ):
    print('submit log entry request()', flush=True)
    # Stops an error message when callback is called during start up.
    if input_box_value is not None :
        print('creating request', flush=True)
        # Create log entry request from input data
        log_entry_request = Log_Entry_Request(dataset_dropdown_value, model_dropdown_value, input_box_value)

        # If the log entry request is valid
        if (log_entry_request.dataset in dataset_choices
            and log_entry_request.model in model_choices
            and log_entry_request.check_valid_ratio()):
            print('log entry request is valid')
            # Create a log entry
            log_entry = create_log_entry(log_entry_request)
            # Add it to the log book
            log_entry_dict[str(log_entry.date) + ' ' + log_entry.dataset] = log_entry
            log_book.append_log_entry(log_entry)
            # Print the log book to the console (for debugging)
            #print_log_book()
            # Update the logbook on the screen
            return 0, [{'label': i, 'value': i} for i in log_entry_dict]

        else:
            print('***log entry could not be created at submit_log_entry_request()***')
            print('dataset', log_entry_request.dataset,
                    'model', log_entry_request.model,
                    'ratio', log_entry_request.check_valid_ratio())
            # Update the logbook on the screen
            return 0, [{'label': i, 'value': i} for i in log_entry_dict]

    else:
        print('Request input type was none')
        # Update the logbook on the screen
        return 0, [{'label': i, 'value': i} for i in log_entry_dict]


# Changed model options displayed depending on dataset chosen
@app.callback(
    Output('Model-dropdown','options'),
    [Input('Dataset-dropdown','value')]
)
def update_model_list(dataset):
    if dataset == None:
        return [{'label': 'Select a dataset first','value': -1}]
    else:
        return [{'label': i, 'value': i} for i in model_dict[dataset]]


# Callback for  the text area (notes)
@app.callback(
    Output('textarea', 'style'),
    [Input('textarea-button', 'n_clicks')],
    [State('textarea', 'value')]
)
def update_output(n_clicks, value):
    if log_book.selected_log_entry is not None:
        print(log_book.selected_log_entry.date, flush = True)
        log_book.selected_log_entry.notes = value
        return {'width': '100%', 'height': 300, 'display': 'flex'}
    return {'width': '100%', 'height': 300, 'display': 'flex'}



if __name__ == '__main__':
    app.run_server(debug=True)
