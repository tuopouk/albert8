#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the necessary libraries

import pandas as pd
import numpy as np
import math
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from flask import Flask
import os




server = Flask(__name__)
server.secret_key = os.environ.get('secret_key','secret')
app = dash.Dash(name = __name__, server = server,prevent_initial_callbacks=False)


app.title = 'Albert 8 - Compound Interest Calculator'

def compound_funds(seed_capital = 100, 
                   monthly_savings = 100, 
                   expected_yearly_profit = .06, 
                   saving_years = 5, 
                   yearly_expenses = .02,
                 
                   inflation = .02):
    
    
    monthly_profit = expected_yearly_profit/12

    
    
    monthly_expenses = yearly_expenses/12
    
    monthly_inflation = inflation/12

    compound = seed_capital
    zero_expense_compound = seed_capital
    bank = seed_capital
    bank_inflation = seed_capital
    inflation_compound = seed_capital
    zero_expense_inflation_compound = seed_capital
    months_saved = 0
    years_saved = 0
    compound_list=[]

    
    for i in range(12 * saving_years):
        
        
        # Compound with profit
        
        zero_expense_compound = zero_expense_compound * (1 + monthly_profit)
        zero_expense_compound = zero_expense_compound + monthly_savings
        
        # Compound with profit margin (profit - expenses)
        
        compound = compound * (1 + monthly_profit - monthly_expenses)
        compound = compound + monthly_savings
        
        # Bank deposit
        
        bank = bank + monthly_savings
        
        
        # Compound with profit (inflation andjusted)
        
        zero_expense_inflation_compound = zero_expense_inflation_compound * (1 + monthly_profit)
        zero_expense_inflation_compound = zero_expense_inflation_compound * (1 - monthly_inflation)
        zero_expense_inflation_compound = zero_expense_inflation_compound + monthly_savings
        
        
        # Compound with profit margin (inflation andjusted)
        
        inflation_compound = inflation_compound * (1 + monthly_profit - monthly_expenses) 
        inflation_compound = inflation_compound * (1 - monthly_inflation)
        inflation_compound = inflation_compound + monthly_savings
        

        # Bank deposit (inflation adjusted)

        
        bank_inflation = bank_inflation * (1 - monthly_inflation)
        bank_inflation = bank_inflation + monthly_savings
        

        months_saved +=1
        
        
        if (i+1)%12 == 0:
            years_saved+=1
            compound_list.append({'years_saved':years_saved, 'compound':compound, 'inflation_compound':inflation_compound, 'zero_expense_compound':zero_expense_compound,'bank_inflation':bank_inflation,'zero_expense_inflation_compound':zero_expense_inflation_compound, 'bank':bank})
            

        
    compound_df = pd.DataFrame(compound_list)

        
    return compound_df

@app.callback(
    Output('plot', 'children'),
    [Input('seed', 'value'),
     Input('savings', 'value'),
     Input('profit', 'value'),
     Input('years', 'value'),
     Input('expenses', 'value'),
     Input('inflation', 'value'),
     Input('currency','value')
    ])
def plot_compound(seed, savings, profit, years, expenses,  inflation_rate, currency):
    

    
        compound_df = compound_funds(seed_capital = seed, monthly_savings = savings, expected_yearly_profit = profit/100,
                            saving_years = years, yearly_expenses = expenses/100,  inflation = inflation_rate/100)
        
        
        compound_hover = ['{} '.format(
                                                                                                                                      '{:,}'.format(round(compound_df.iloc[i].zero_expense_compound,2)).replace(',',' ')+currency)
         for i in range(len(compound_df))]
        
        expense_hover = ['{} '.format(
                                                                                                                                     
       '{:,}'.format(round(compound_df.iloc[i].compound,2)).replace(',',' ')+currency)

         for i in range(len(compound_df))]
        
        bank_hover = ['{} '.format(

        '{:,}'.format(round(compound_df.iloc[i].bank,2)).replace(',',' ')+currency)
         for i in range(len(compound_df))]
        
        zero_expense_inflation_hover = ['{} '.format(
                                                                                                                                      '{:,}'.format(round(compound_df.iloc[i].zero_expense_inflation_compound,2)).replace(',',' ')+currency)
         for i in range(len(compound_df))]
        
        expense_inflation_hover = ['{} '.format(
                                                                                                                                     
       '{:,}'.format(round(compound_df.iloc[i].inflation_compound,2)).replace(',',' ')+currency)

         for i in range(len(compound_df))]
        
        bank_inflation_hover = ['{} '.format(

        '{:,}'.format(round(compound_df.iloc[i].bank_inflation,2)).replace(',',' ')+currency)
         for i in range(len(compound_df))]
        
        
        last_compound = '{:,}'.format(np.round(compound_df.tail(1).zero_expense_compound.values[0],2)).replace(',',' ')
        last_expensed_compound = '{:,}'.format(np.round(compound_df.tail(1).compound.values[0],2)).replace(',',' ')
        diff = '{:,}'.format(np.round(compound_df.tail(1).zero_expense_compound.values[0]-compound_df.tail(1).compound.values[0],2)).replace(',',' ')
        
        

            
        return html.Div(children = [dcc.Graph(animate=False, figure = go.Figure(data=[
            
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.zero_expense_compound,2), name = 'Invested compound funds', marker = dict(color = 'blue'),mode='lines+markers',hovertemplate=compound_hover),
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.compound,2), name = 'Invested compound funds with expenses', marker = dict(color = 'orange'),mode='lines+markers', hovertemplate=expense_hover),
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.bank,2), name = 'Compound bank deposits', marker = dict(color = 'red'),mode='lines+markers',hovertemplate=bank_hover)
        ],
                       layout = go.Layout(title = dict(text="Investment plans' annual values ({})".format(currency),x=.5),
                                         xaxis = dict(title='Time'),
                                         yaxis = dict(title='Annual value ({})'.format(currency), tickformat=' '),
                                          legend=dict(
                                                                                                orientation="h",
                                                                                                yanchor="top",
                                                                                                y=0.99,
                                                                                                xanchor="center",
                                                                                                x=0.5,
                                                                                                title_font_family = 'Arial',
                                                                                               font = dict(family='Arial',
                                                                                                           size=14,
                                                                                                           color='black'),
                                                                                               bgcolor = 'white',
                                                                                               bordercolor = 'Black',
                                                                                               borderwidth=2),
                                          height=700,hovermode="x unified"
                                         )
                                                         )
                                      ),
                                    
                           
             
                                    
                                    
                                    
                                    
                                    
                                    
                                    html.P('Compound funds after {} years: {}. Compound funds after expenses: {}. Expenses devalue the compound funds by: {}'.format(years,last_compound+currency,last_expensed_compound+currency,diff+currency),style=dict(textAlign='center',fontSize=22, fontFamily='Arial')),
                                    
                                    
                                    dcc.Graph(animate=False, figure = go.Figure(data=[
            
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.zero_expense_inflation_compound,2), name = 'Invested compound funds (with inflation)', marker = dict(color = 'blue'),mode='lines+markers',hovertemplate=zero_expense_inflation_hover),
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.inflation_compound,2), name = 'Invested compound funds with expenses (with inflation)', marker = dict(color = 'orange'),mode='lines+markers', hovertemplate=expense_inflation_hover),
            go.Scatter(x=[str(i)+'. year' for i in compound_df.years_saved],
                      y = np.round(compound_df.bank_inflation,2), name = 'Compound bank deposits (with inflation)', marker = dict(color = 'red'),mode='lines+markers',hovertemplate=bank_inflation_hover)
        ],
                       layout = go.Layout(title = dict(text="Investment plans' annual values ({} with inflation)".format(currency),x=.5),
                                         xaxis = dict(title='Time'),
                                         yaxis = dict(title='Annual value ({})'.format(currency), tickformat=' '),
                                          legend=dict(
                                                                                                orientation="h",
                                                                                                yanchor="top",
                                                                                                y=0.99,
                                                                                                xanchor="center",
                                                                                                x=0.5,
                                                                                                title_font_family = 'Arial',
                                                                                               font = dict(family='Arial',
                                                                                                           size=14,
                                                                                                           color='black'),
                                                                                               bgcolor = 'white',
                                                                                               bordercolor = 'Black',
                                                                                               borderwidth=2),
                                          height=700,hovermode="x unified"
                                         )
                                                         )
                                      )
                                    
#                                     html.P('Compound funds after {} years: {}. Compound funds after expenses: {}. Expenses devalue the compound funds by: {}'.format(years,last_compound+currency,last_expensed_compound+currency,diff+currency),style=dict(textAlign='center',fontSize=22, fontFamily='Arial'))
                                    
                                    
#                                                                         html.P('Compound funds after expenses: {:,}'.format(np.round(last_expensed_compound,2)).replace(',',' ')+currency),
#                                     html.P('Expenses: {:,}'.format(np.round(last_compound-last_expensed_compound,2)).replace(',',' ')+currency)
#                                     html.P('Compound funds after {} years if savings were in a zero-interest bank account.: {:,}'.format(years,np.round(compound_df.tail(1).bank.values[0],2)).replace(',',' ')+currency)
                            ]
                )
    
    
@app.callback(
    Output('seed-container', 'children'),
    [Input('seed', 'value'),Input('currency','value')])
def update_seed_output(value,currency):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+currency)

@app.callback(
    Output('savings-container', 'children'),
    [Input('savings', 'value'),Input('currency','value')])
def update_savings_output(value,currency):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+currency) 

@app.callback(
    Output('profit-container', 'children'),
    [Input('profit', 'value')])
def update_profit_output(value):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+'%') 

@app.callback(
    Output('years-container', 'children'),
    [Input('years', 'value')])
def update_years_output(value):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+' year-plan') 
@app.callback(
    Output('expenses-container', 'children'),
    [Input('expenses', 'value')])
def update_expenses_output(value):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+'%') 
@app.callback(
    Output('inflation-container', 'children'),
    [Input('inflation', 'value')])
def update_inflation_output(value):
    return '{}'.format('{:,}'.format(value).replace(',',' ')+'%') 
       

def serve_layout():
    return html.Div(children = [
    
         #html.Div(children=[
          #  html.Div(children=[
                
                html.H3('Select your currency.'),
                dcc.RadioItems(id = 'currency',    
                               options=[
        {'label': '€', 'value': '€'},
        {'label': '$', 'value': '$'},
        {'label': '£', 'value': '£'},
         {'label': '¥', 'value': '¥'}                          
                                   
    ],
    value='€',
    labelStyle={'display': 'inline-block'}),
                
                html.H3('Select your current seed capital.'),
                dcc.Slider(id = 'seed',
                                   min = 0,
                                   max = 100000,
                                   value = 1000,
                                   step =1,
                                   marks = {
                                       1000: '1 000',
                                       5000: '5 000',
                                       10000: '10 000'
                                   
                                   }

                                         ),
                 html.Div(id='seed-container'),

                     
           # ]),
        
        
            #html.Div(children=[
                html.H3('Select your monthly savings.'),
                             
                dcc.Slider(id = 'savings',
                                         min = 0,
                                         max = 2000,
                                         value = 15,
                                         step = 1,
                                          marks = {
                                           0: '0',
                                           
                                           
                                           500: '500',
                                           2000: '2 000'#,
                                          # 10000: '10 000'
                                   
                                           }
                                   
                                         ),
                html.Div(id='savings-container'),
               # ]),
      #  ]),
        
        #html.Div(children=[
           # html.Div(children=[
            html.H3('Select your yearly expected profit.'),
                             
            dcc.Slider(id = 'profit',
                                         min = 0,
                                         max = 100,
                                         value = 9.9,
                                        step = 0.1,
                                        marks = {
                                            0: '0%',
                                            
                                            10:'10%',
                                            50: '50%',
                                            100: '100%'
                                        }
                                   
                                         ),
            html.Div(id='profit-container'),
                        # ]),
          #  html.Div(className='three columns',children=[
                html.H3('Select your saving years.'),
                             
                dcc.Slider(id = 'years',
                                         min = 1,
                                         max = 70,
                                         value = 5,
                                        step =1,
                                       marks={
                                           1: '1 year',
                                           10: '10 years',
                                           15: '15 years',
                                           20: '20 years',
                                           30: '30 years',
                                           70: '70 years'
                                       
                                       }
                                   
                                         ),
                html.Div(id='years-container'),
                       #  ]),
       #html.Div(children=[ 
       #html.Div(children=[
                             html.H3('Select your yearly expenses.'),
                             
                             dcc.Slider(id = 'expenses',
                                         min = 0,
                                         max = 5,
                                         value = 0.2,
                                        step = 0.01,
                                        marks = {
                                            0 : '0%',
                                            1.5: '1.5%',
                                            5: '5%'
                                        
                                        }
                                   
                                         ),
                            html.Div(id='expenses-container'),
                       #  ]),
        
       # html.Div( children=[

            
             #html.Div( children=[
                             html.H3('Select yearly inflation.'),
                             dcc.Slider(id = 'inflation',
                                         min = 0,
                                         max = 10,
                                         value = 2,
                                        step = 0.1,
                                        marks = {
                                            0: '0%',
                                            2: '2%',
                                            5: '5%',
                                            10: '10%'
                                        
                                        }
                                   
                                         ),
                        html.Div(id='inflation-container'),
             
          #   ])
        
        
      # ]),
        html.Div(id = 'plot')
        
    
       
        ])


app.layout = serve_layout
# Run app.
if __name__ == '__main__':
    app.run_server(debug=False)   
