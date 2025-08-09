from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
import yfinance as yf
import plotly.graph_objs as go
from plotly.offline import plot
from datetime import datetime, timedelta
from .models import StockQuote
import numpy as np

def fetch_and_store_quotes(ticker, start_date, end_date):
    df = yf.download(ticker, start=start_date, end=end_date)

    if df.empty:
        print(f"No data found for {ticker}")
        return
    
    ticker = ticker.upper()

    for date, row in df.iterrows():
        StockQuote.objects.update_or_create(
            ticker=ticker,
            date=date.date(),
            defaults={
                'open': row['Open'][ticker],
                'high': row['High'][ticker],
                'low': row['Low'][ticker],
                'close': row['Close'][ticker],
                'volume': row['Volume'][ticker],
            }
        )

def query_data_range(ticker, start, end):
    queryset = StockQuote.objects.filter(ticker=ticker.upper())

    if start:
        queryset = queryset.filter(date__gte=start)
    if end:
        queryset = queryset.filter(date__lte=end)
    return queryset

def return_data_len(ticker, start, end):
    queryset = query_data_range(ticker, start, end)
    q_len = 0

    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    if queryset.count() < 1:
        fetch_and_store_quotes(ticker, start, end)
        return query_data_range(ticker, start, end)
    
    db_start_date = queryset.values()[0]['date']
    db_end_date = queryset.values()[queryset.count()-1]['date']
    # Calculate difference
    delta = (db_start_date- start_date ).days
    refetch =False
    if delta > 4:
        fetch_and_store_quotes(ticker, start, db_start_date)
        refetch =True

    delta = (end_date-db_end_date).days
    if delta > 4:
        fetch_and_store_quotes(ticker, db_end_date, end_date)
        refetch =True

    try:
        q_len=len(queryset)
    except:
        return {}
    q_delta = abs(delta - q_len)
    if not q_len or refetch:
        return query_data_range(ticker, start, end)
    return queryset

def calculate_rsi(data, period=14):
   
    close_prices = np.array( data)
    deltas =  np.diff(close_prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.empty_like(close_prices)
    avg_loss = np.empty_like(close_prices)

    avg_gain[:period] = 0
    avg_loss[:period] = 0

    # First average gain/loss are simple means
    avg_gain[period] = gains[:period].mean()
    avg_loss[period] = losses[:period].mean()   
    
    # Calculate smoothed average gain/loss
    for i in range(period + 1, len(close_prices)):
        avg_gain[i] = (avg_gain[i-1] * (period - 1) + gains[i-1]) / period
        avg_loss[i] = (avg_loss[i-1] * (period - 1) + losses[i-1]) / period
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi[:period] =0

    rsi_colors = ['green' if r < 30 else 'red' if r > 70 else 'black' for r in rsi]
    return rsi, rsi_colors


def create_bars(open, close):
    close_prices = np.array( close)
    open_prices = np.array( open)
    diffs = np.diff(close_prices)
    lengths = list(np.abs(diffs))
    colors = ['green' if d > 0 else 'red' for d in diffs]
    start_point = [c if c> o else o for c, o in zip(close,open)]
    return start_point, lengths, colors



@api_view(['POST'])
def candle_stick_data(request):
    queryset=get_query_start_end(request)
    if queryset is None: 
        return Response({'error': 'No data found'}, status=404)
    # Format the response with dates and prices
    dates_str =[d['date'].strftime('%Y-%m-%d') for d in queryset.values('date')]
    prices_close = [d['close'] for d in queryset.values('close')]
    prices_open = [d['open'] for d in queryset.values('open')]
    prices_high = [d['high'] for d in queryset.values('high')]
    prices_low = [d['low'] for d in queryset.values('low')]
  
    
    response_data = {
        'dates_str': dates_str,
        'open_prices':prices_open,
        'close_prices':prices_close,
        'high_prices':prices_high,
        'prices_low':prices_low,
    }

    return Response(response_data)

@api_view(['POST'])
def rsi_plot(request):    


    ticker = request.data.get("ticker", "AAPL")
    start = request.data.get("start")
    end = request.data.get("end")
    rsi_period = request.data.get("rsi_period")
    print("ticker",ticker)
    rsi_period_pad=rsi_period*3
    if not end:
        end = datetime.today().strftime('%Y-%m-%d')
    if not start:
        start = (datetime.strptime(end, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

    start_padded=(datetime.strptime(start, '%Y-%m-%d') -timedelta(days=rsi_period_pad)).strftime('%Y-%m-%d')

    # Download data
    # data = yf.download(ticker, start=start, end=end)

    queryset=return_data_len(ticker, start_padded, end)
    if not queryset.count(): 
        return Response({'error': 'No data found'}, status=404)

    # data = queryset.values('date', 'open', 'high', 'low', 'close', 'volume')
    if not queryset.count():
        return Response({'error': 'No data found'}, status=404)
    # data = queryset.values('date', 'open', 'high', 'low', 'close', 'volume')
    # Format the response with dates and prices
    dates_str =[d['date'].strftime('%Y-%m-%d') for d in queryset.values('date')]
    idx_start_date =None
    for i in range(rsi_period_pad):

        try:
            idx_start_date = dates_str.index(start)
        except:
            start = (datetime.strptime(start, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

        if idx_start_date is not None:
            break

    if idx_start_date is None or idx_start_date < rsi_period:
        Response(status=501, context="please try another date, market seemed closed over to long a period. Could no sufficiently pad the date period")
    prices_close = [d['close'] for d in queryset.values('close')]

    rsi_data, rsi_colors = calculate_rsi(prices_close,rsi_period)
    # prices_close=prices_close[rsi_period:]
    # prices_open=prices_open[rsi_period:]
    rsi_data=rsi_data[idx_start_date:]
    dates_str=dates_str[idx_start_date:]
    
    response_data = {
        'rsi':rsi_data,
        'rsi_dates':dates_str,
        'rsi_colors':rsi_colors,
    }

    return Response(response_data)

def get_query_start_end(request):
    ticker = request.data.get("ticker", "AAPL")
    start = request.data.get("start")
    end = request.data.get("end")
    print("ticker",ticker)
    if not end:
        end = datetime.today().strftime('%Y-%m-%d')
    if not start:
        start = (datetime.strptime(end, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

    # Download data
    # data = yf.download(ticker, start=start, end=end)

    queryset=return_data_len(ticker, start, end)
    if not queryset.count(): 
        return None
    
    return queryset


@api_view(['POST'])
def stock_plot(request):    
    # ticker = request.data.get("ticker", "AAPL")
    # start = request.data.get("start")
    # end = request.data.get("end")
    # print("ticker",ticker)
    # if not end:
    #     end = datetime.today().strftime('%Y-%m-%d')
    # if not start:
    #     start = (datetime.strptime(end, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

    # # Download data
    # # data = yf.download(ticker, start=start, end=end)

    queryset=get_query_start_end(request)
    if queryset is None: 
        return Response({'error': 'No data found'}, status=404)

    # data = queryset.values('date', 'open', 'high', 'low', 'close', 'volume')
    rsi_period = 14
    if not queryset.count():
        return Response({'error': 'No data found'}, status=404)
    data = queryset.values('date', 'open', 'high', 'low', 'close', 'volume')
    # Format the response with dates and prices
    dates_str =[d['date'].strftime('%Y-%m-%d') for d in queryset.values('date')]
    prices_close = [d['close'] for d in queryset.values('close')]
    prices_open = [d['open'] for d in queryset.values('open')]
    # prices_high = [d['high'] for d in queryset.values('high')]
    # prices_low = [d['low'] for d in queryset.values('low')]
    # rsi_data, rsi_colors = calculate_rsi(prices_close,rsi_period)
    # prices_close=prices_close[rsi_period:]
    # prices_open=prices_open[rsi_period:]
    start_point, lengths, colors=create_bars(prices_open, prices_close)
   
    
    response_data = {
        'dates': dates_str,
        # 'rsi':rsi_data,
        'rsi_dates':dates_str[rsi_period:],
        'prices_close':prices_close,
        'bar_start':start_point, 
        'bar_lengths':lengths, 
        'bar_colors':colors
    }

    return Response(response_data)
