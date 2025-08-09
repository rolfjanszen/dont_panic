from django.urls import path
from .views import stock_plot, candle_stick_data

urlpatterns = [
    path('stock/', stock_plot),
    path('candle_stick/', candle_stick_data),
]
