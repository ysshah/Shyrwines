# Shyrwines

## Instructions for local development

1. Create a blank settings_local.py file in the [shyrwines](shyrwines) directory
2. Run `python manage.py migrate`
3. Add wines to database using [sync.py](shyr/management/commands/sync.py)
4. [Optional] Add wine images as shyr/static/wines/[SKU].jpg
5. [Optional] Add wine factsheets as shyr/static/factsheets/[SKU].pdf
6. Run `python manage.py runserver`
