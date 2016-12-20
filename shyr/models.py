from django.db import models

class Wine(models.Model):
    name = models.CharField(max_length=128, unique=True)
    count = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    sku = models.PositiveIntegerField(unique=True)
    vintage = models.PositiveSmallIntegerField(null=True)
    winery = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    region = models.CharField(max_length=128, null=True)
    appellation = models.CharField(max_length=128, null=True)
    varietal = models.CharField(max_length=128, null=True)
    wine_type = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=2048, null=True)

    JH = models.PositiveSmallIntegerField('James Halliday', null=True)
    JS = models.PositiveSmallIntegerField('James Suckling', null=True)
    RP = models.PositiveSmallIntegerField('Robert Parker', null=True)
    ST = models.PositiveSmallIntegerField('Stephen Tanzer', null=True)
    AG = models.PositiveSmallIntegerField('Antonio Galloni', null=True)
    D = models.PositiveSmallIntegerField('Decanter', null=True)
    WA = models.PositiveSmallIntegerField('Wine Advocate', null=True)
    WE = models.PositiveSmallIntegerField('Wine Enthusiast', null=True)
    WS = models.PositiveSmallIntegerField('Wine Spectator', null=True)
    WandS = models.PositiveSmallIntegerField('Wine & Spirits', null=True)
    WW = models.PositiveSmallIntegerField('Wilfred Wong', null=True)

    def __str__(self):
        return self.name
