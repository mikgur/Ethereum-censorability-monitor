from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import plotly.express as px
from plotly.offline import plot
import requests

def index(request):
    
    req = requests.get('http://127.0.0.1:8001/data')
    df = pd.read_json(req.json())
    
    barplot = px.bar(
        df,
        x="tx_hash", y="validator_name",
        color = 'is_ofac',
        orientation="h",
        barmode = 'group',
        title='Share of all transactions (OFAC - NON OFAC transactions)',
        labels={
                    "validator_name": "Validator",
                    "tx_hash": "Share of all transactions (OFAC - NON OFAC transactions)",
                    "is_ofac": "Type of transaction"
                }
    )
    
    plot_div = plot(barplot,output_type='div')
    
    return render(request, "index.html", context={'plot_div': plot_div})