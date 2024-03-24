from django.db import models


class Crypto(models.Model):
    """
    Model representing a cryptocurrency.
    """
    pair = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.pair}"


class PriceData(models.Model):
    """
    Model representing historical price data for cryptocurrencies.
    """
    pair = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    open_time = models.DateTimeField()
    close_time = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pair} - {self.open_time} to {self.close_time}"


class BubbleDuration(models.Model):
    """
    Model representing the duration of a price bubble for a cryptocurrency.
    """
    pair = models.ForeignKey(Crypto, on_delete=models.CASCADE)
    # data_start = models.DateTimeField()
    # data_end = models.DateTimeField()
    # bubble_start = models.DateTimeField()
    # bubble_end = models.DateTimeField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pair} - Bubble from {self.start_date} to {self.end_date}"
