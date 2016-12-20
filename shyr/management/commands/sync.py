from django.core.management.base import BaseCommand
from shyr.models import Wine
import os
import sys
import numpy as np
import pandas as pd
from colorama import init, Fore, Style

RED, GREEN, BLUE, RESET_ALL = Fore.RED, Fore.GREEN, Fore.BLUE, Style.RESET_ALL

class Command(BaseCommand):
    help = 'Sync the Wine database with the Shyr Wine List Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('excelFile',
            help='Path to Shyr Wine List Excel file')

    def handle(self, *args, **options):
        # Required columns
        required = np.array(['Name', 'Price', 'SKU', 'Vintage', 'Winery',
            'Country', 'Varietal', 'Type'])

        # Read Shyr Wine List and check if missing required columns
        df = pd.read_excel(os.path.expanduser(options['excelFile']))
        if df[required].isnull().any().any():
            for i in df.index[df[required].isnull().any(axis=1)]:
                print('Error: Row {} is missing {}'.format(i,
                    required[np.where(df.loc[i][required].isnull())[0]]))
            sys.exit(1)

        # Fill empty counts with 1
        df['Count'] = df['Count'].fillna(1).astype(int)

        df = df.where((pd.notnull(df)), None)

        changed = False
        for i, r in df.iterrows():
            new = {
                'name': r.Name,
                'count': r.Count,
                'price': r.Price,
                'vintage': int(r.Vintage) if r.Vintage != 'NV' else None,
                'winery': r.Winery,
                'country': r.Country,
                'region': r.Region,
                'appellation': r.Appellation,
                'varietal': r.Varietal,
                'wine_type': r.Type,
                'description': r.Description,
                'JH': r.JH,
                'JS': r.JS,
                'RP': r.RP,
                'ST': r.ST,
                'AG': r.AG,
                'D': r.D,
                'WA': r.WA,
                'WE': r.WE,
                'WS': r.WS,
                'WandS': r.WandS,
                'WW': r.WW
            }

            if Wine.objects.filter(sku=r.SKU).exists():
                wine = Wine.objects.filter(sku=r.SKU)
                old = wine.values(*new.keys())[0]
                old['price'] = float(old['price'])  # Decimal -> float conversion
                diffKeys = [k for k in old if old[k] != new[k]]
                if diffKeys:
                    print('\nSKU {}: {}'.format(r.SKU, old['name']))
                    for k in diffKeys:
                        print('    Change {}{}{}\n        {}{}{}\n        {}{}{}'.format(
                            BLUE, k, RESET_ALL, RED, old[k], RESET_ALL, GREEN, new[k], RESET_ALL))
                    wine.update(**{k: new[k] for k in diffKeys})
                    changed = True
            else:
                new['sku'] = r.SKU
                print('New SKU {}: {}'.format(new['sku'], new['name']))
                Wine(**new).save()
                changed = True

        if not changed:
            print('No differences.')
