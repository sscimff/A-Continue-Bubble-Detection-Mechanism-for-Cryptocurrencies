import os
from django.http import Http404
from django.shortcuts import render
import requests
from .models import BubbleDuration, Crypto, PriceData
import plotly.graph_objects as go
import pandas as pd
from django.utils import timezone

def crypto_list(request):
    crypto_list = Crypto.objects.all()

    crypto_data = []
    # Iterate over each cryptocurrency in crypto_list
    for crypto in crypto_list:
        pair = crypto.pair
        # Append the Crypto object and its corresponding price to crypto_data
        symbol = crypto.pair[:3].lower()
        # Make an API request to get the price
        api_url = f"https://api.api-ninjas.com/v1/cryptoprice?symbol={pair}"
        REAL_TIME_PRICE_API_KEY = os.getenv("REAL_TIME_PRICE_API_KEY")
        response = requests.get(
            api_url, headers={'X-Api-Key': REAL_TIME_PRICE_API_KEY})

        # Extract the price from the API response
        if response.status_code == requests.codes.ok:
            price_data = response.json()
            price = price_data.get('price')
        else:
            price = response.text  # Set price as 'N/A' if API request fails

        crypto_data.append((pair, price, symbol))

    # Pass the combined data to the template context
    context = {'crypto_data': crypto_data}
    return render(request, "crypto/index.html", context)

def chart(request):
    pair = request.GET.get('pair', None)
    if not pair:
        raise Http404("Pair parameter is missing")
    
    # Get the price data from the database by pair
    price_data = PriceData.objects.filter(pair__pair=pair)

    # Extract the earliest and latest dates
    earliest_data = price_data.order_by('open_time').first()
    latest_data = price_data.order_by('-open_time').first()
    earliest_date = timezone.localtime(earliest_data.open_time).strftime('%Y-%m-%dT%H:%M')
    latest_date = timezone.localtime(latest_data.open_time).strftime('%Y-%m-%dT%H:%M')

    # Define bubble data
    bubble_data = BubbleDuration.objects.filter(pair__pair=pair)

    # Create a list of shapes for bubble durations
    bubble_shape = []
    for duration in bubble_data:
        bubble_shape.append({
            'type': 'rect',
            'xref': 'x',
            'yref': 'paper',
            'x0': duration.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'y0': 0,
            'x1': duration.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'y1': 1,
            'fillcolor': 'rgba(255, 0, 0, 0.5)',
            'line': {'width': 0},
            'layer': 'below'
        })

    # Create the candlestick chart
    fig = go.Figure(
        data=[go.Candlestick(
            x=[c.open_time for c in price_data],
            open=[c.open for c in price_data],
            high=[c.high for c in price_data],
            low=[c.low for c in price_data],
            close=[c.close for c in price_data],
        )]
    )

    # Update the layout with bubble shapes
    fig.update_layout(
        width=1015,
        margin=dict(l=15, r=15, t=15, b=15),
        yaxis_title='Price',
        shapes=bubble_shape,
    )

    # Generate HTML for the chart
    chart_html = fig.to_html()

    # Prepare the context to pass to the template
    context = {
        'pair': pair,
        'chart': chart_html,
        'earliest_date': earliest_date,
        'latest_date': latest_date,
    }

    return render(request, 'crypto/crypto_detail.html', context)
