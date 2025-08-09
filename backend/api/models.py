from django.db import models

class StockQuote(models.Model):
    ticker = models.CharField(max_length=10, db_index=True)
    date = models.DateField(db_index=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('ticker', 'date')
        ordering = ['ticker', 'date']

    def __str__(self):
        return f"{self.ticker} - {self.date}"
