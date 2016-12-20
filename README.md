# Shyrwines

## Instructions for local development

1. Run `python manage.py migrate`
2. Add wines to database using [sync.py](shyr/management/commands/sync.py)
3. [Optional] Add wine images as shyr/static/wines/[SKU].jpg
4. [Optional] Add wine factsheets as shyr/static/factsheets/[SKU].pdf
5. Run `python manage.py runserver`
