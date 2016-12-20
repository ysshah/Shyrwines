from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.staticfiles import finders
from .ajax import getCartContext, getAllWinesContext
from .models import Wine

raters = (
    ('JH', 'James Halliday'),
    ('JS', 'James Suckling'),
    ('RP', 'Robert Parker'),
    ('ST', 'Stephen Tanzer'),
    ('AG', 'Antonio Galloni'),
    ('D', 'Decanter'),
    ('WA', 'Wine Advocate'),
    ('WE', 'Wine Enthusiast'),
    ('WS', 'Wine Spectator'),
    ('WandS', 'Wine & Spirits'),
    ('WW', 'Wilfred Wong')
)

def _get_ratings(this_wine):
    ratings = []
    for rater_abbr, rater_full in raters:
        if getattr(this_wine, rater_abbr):
            ratings.append((rater_full, getattr(this_wine, rater_abbr)))
    return ratings


def about(request):
    return render(request, 'about.html', {'page_title': 'About | '})


def all_wines(request):
    return render(request, 'all-wines.html', getAllWinesContext(request))


def index(request):
    varietal_panels = [
        ("?varietal=Cabernet Sauvignon", "Cabernet Sauvignon", "cabernet.jpg"),
        ("?varietal=Syrah", "Syrah", "syrah.jpg"),
        ("?varietal=Zinfandel", "Zinfandel", "zinfandel.jpg"),
        ("?varietal=Pinot Noir", "Pinot Noir", "pinot.jpg")
    ]
    country_panels = [
        ("?country=USA", "American", "usa.jpg"),
        ("?country=Italy", "Italian", "italy.jpg"),
        ("?country=Spain", "Spanish", "spain.jpg"),
        ("?country=France", "French", "france.jpg")
    ]
    context = {
        'varietal_panels': varietal_panels,
        'country_panels': country_panels
    }
    return render(request, 'index.html', context)


def cart(request):
    return render(request, 'cart.html', getCartContext(request))


def contact_us(request):
    return render(request, 'contact-us.html',
        {'page_title': 'Contact Us | '})


def privacy_policy(request):
    return render(request, 'privacy-policy.html',
        {'page_title': 'Privacy Policy | '})


def terms_of_service(request):
    return render(request, 'terms-of-service.html',
        {'page_title': 'Terms of Service | '})


def view(request, wine_id):
    wine = get_object_or_404(Wine, pk=wine_id)
    image_exists = finders.find('wines/{}.jpg'.format(wine.sku))
    factsheet_exists = finders.find('factsheets/{}.pdf'.format(wine.sku))
    context = {
        'page_title': wine.name + ' | ',
        'wine': wine,
        'image_exists': image_exists,
        'factsheet_exists': factsheet_exists,
        'ratings': _get_ratings(wine)
    }
    return render(request, 'view.html', context)
