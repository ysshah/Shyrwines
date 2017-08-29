import os
import sys

from colorama import Fore, Style
from django.core.management.base import BaseCommand
import numpy as np
import pandas as pd

from shyr.models import Wine


RED, GREEN, BLUE, RESET_ALL = Fore.RED, Fore.GREEN, Fore.BLUE, Style.RESET_ALL


class Command(BaseCommand):
    help = 'Sync the Wine database with the Shyr Wine List Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('excelFile', help='Path to Shyr Wine List Excel file')
        parser.add_argument('--check', action='store_true', help='Only check differences, do not sync.')

    def handle(self, *args, **options):
        # Required columns
        required = np.array(['Name', 'Price', 'SKU', 'Vintage', 'Winery',
                             'Country', 'Varietal', 'Type'])

        # Read Shyr Wine List and check if missing required columns
        df = pd.read_excel(os.path.expanduser(options['excelFile']))
        if df[df['No-Adv'] != 'N'][required].isnull().any().any():
            for i in df.index[df[required].isnull().any(axis=1)]:
                print('{}Error: Row {} "{}" is missing {}{}'.format(RED, i+2, df.at[i, 'Name'],
                      required[np.where(df.loc[i][required].isnull())[0]], RESET_ALL))
            sys.exit(0)

        # Fill empty counts with 1
        df['Count'] = df['Count'].fillna(1).astype(int)

        df = df.where((pd.notnull(df)), None)

        num_inserts, num_updates = 0, 0
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
                if r['No-Adv'] == 'N':
                    print('\nRemove SKU {}: {}'.format(r.SKU, new['name']))
                    if not options['check']:
                        wine.delete()
                else:
                    old = wine.values(*new.keys()).first()
                    old['price'] = float(old['price'])  # Decimal -> float conversion
                    diff_keys = [k for k in old if old[k] != new[k]]
                    if diff_keys:
                        print('\nSKU {}: {}'.format(r.SKU, old['name']))
                        for k in diff_keys:
                            print('    Change {}{}{}\n        {}{}{}\n        {}{}{}'.format(
                                BLUE, k, RESET_ALL, RED, old[k], RESET_ALL, GREEN, new[k], RESET_ALL))
                        if not options['check']:
                            wine.update(**{k: new[k] for k in diff_keys})
                        num_updates += 1
            elif r['No-Adv'] != 'N':
                new['sku'] = r.SKU
                print('\nNew SKU {}: {}'.format(new['sku'], new['name']))
                if not options['check']:
                    Wine(**new).save()
                num_inserts += 1

        if num_inserts + num_updates == 0:
            print('No differences.')
        else:
            print('\n{} updates, {} inserts.'.format(num_updates, num_inserts))
