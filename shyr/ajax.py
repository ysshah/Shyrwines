from collections import OrderedDict
from decimal import Decimal

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.template.loader import render_to_string

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

filter_fields = OrderedDict([
    ('country', 'Country'),
    ('region', 'Region'),
    ('appellation', 'Appellation'),
    ('varietal', 'Varietal'),
    ('wine_type', 'Type')
])

sort_options = (
    'Alphabetical: A to Z',
    'Alphabetical: Z to A',
    'Vintage: Old to New',
    'Vintage: New to Old',
    'Price: Low to High',
    'Price: High to Low'
)

price_options = (
    'Less than $20',
    '$20 - $50',
    '$50 - $100',
    'More than $100'
)


def _attach_ratings(wines):
    for wine in wines:
        ratings = []
        for rater_abbr, rater_full in raters:
            if getattr(wine, rater_abbr):
                ratings.append((rater_abbr, getattr(wine, rater_abbr)))
        wine.ratings = ratings
        wine.image_exists = finders.find('images/wines/{}.jpg'.format(wine.sku))


def getCartContext(request):
    context = {'page_title': 'Cart | '}
    if 'cart' in request.session:
        subtotal = 0.0
        wines = Wine.objects.filter(id__in=request.session['cart'].keys())
        for wine in wines:
            wine.quantity = request.session['cart'][str(wine.id)]
            wine.total_price = wine.quantity * wine.price
            subtotal += float(wine.total_price)
        context['cart'] = wines
        context['totals'] = [
            ('Subtotal', round(Decimal(str(subtotal)), 2)),
            ('Estimated Tax', round(Decimal(str(subtotal * 0.0875)), 2)),
            ('Total', round(Decimal(str(subtotal * 1.0875)), 2))
        ]
    else:
        context['cart'] = None

    return context


def getAllWinesContext(request):
    filter_args = {}
    selected = []
    not_selected = []
    for field in filter_fields.keys():
        if field in request.GET:
            filter_args[field] = request.GET[field]
            selected.append((field, filter_fields[field], request.GET[field]))
        else:
            not_selected.append(field)

    query = request.GET.get('q')
    if query:
        filter_args['name__contains'] = query

    # Price divisions
    if 'price' in request.GET:
        if request.GET['price'] == price_options[0]:
            low, high = None, 20
        elif request.GET['price'] == price_options[1]:
            low, high = 20, 50
        elif request.GET['price'] == price_options[2]:
            low, high = 50, 100
        elif request.GET['price'] == price_options[3]:
            low, high = 100, None
        if low:
            filter_args['price__gte'] = low
        if high:
            filter_args['price__lte'] = high
        selected.append(('price', 'Price', request.GET['price']))

    wines = Wine.objects.filter(**filter_args)

    choices = []
    for field in not_selected:
        field_choices = wines.order_by(field).values_list(
            field, flat=True).distinct().exclude(**{field: None})
        choices.append((field, filter_fields[field], field_choices))
    choices.append(('price', 'Price', price_options))
    choices.append(('sort', 'Sort', sort_options))

    # Sorting results
    if 'sort' in request.GET:
        if request.GET['sort'] == sort_options[0]:
            wines = sorted(wines,
                key=lambda w: w.name[5:].lower() if w.vintage else w.name.lower())
        elif request.GET['sort'] == sort_options[1]:
            wines = sorted(wines,
                key=lambda w: w.name[5:].lower() if w.vintage else w.name.lower(),
                reverse=True)
        elif request.GET['sort'] == sort_options[2]:
            wines = wines.order_by('vintage')
        elif request.GET['sort'] == sort_options[3]:
            wines = wines.order_by('-vintage')
        elif request.GET['sort'] == sort_options[4]:
            wines = wines.order_by('price')
        elif request.GET['sort'] == sort_options[5]:
            wines = wines.order_by('-price')
        selected.append(('sort', 'Sort', request.GET['sort']))
    else:
        wines = sorted(wines,
            key=lambda w: w.name[5:].lower() if w.vintage else w.name.lower())

    _attach_ratings(wines)

    paginator = Paginator(wines, 15)
    try:
        wines = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        wines = paginator.page(1)
    except EmptyPage:
        wines = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'All Wines | ',
        'query': query,
        'wines': wines,
        'selected': selected,
        'choices': choices
    }
    return context


def add(request):
    if request.is_ajax() and request.GET:
        if 'cart' in request.session:
            request.session['cart'][request.GET['id']] = request.session['cart'].get(
                request.GET['id'], 0) + int(request.GET['quantity'])
            request.session.modified = True
        else:
            request.session['cart'] = {
                request.GET['id']: int(request.GET['quantity'])
            }
        return HttpResponse('1', content_type='application/json')
    else:
        raise Http404


def autocomplete(request):
    if request.is_ajax() and request.GET:
        query = request.GET['q'].lower()
        wines = Wine.objects.filter(name__contains=query)[:5]
        for wine in wines:
            i = wine.name.lower().index(query)
            wine.before = wine.name[:i]
            wine.match = wine.name[i:i + len(query)]
            wine.after = wine.name[i + len(query):]

        matched_fields = []
        for field in filter_fields.keys():
            for match in Wine.objects.values(field).distinct().filter(
                **{field+'__contains':query})[:1]:
                i = match[field].lower().index(query)
                match['fieldname'] = match[field]
                match['before'] = match[field][:i]
                match['match'] = match[field][i:i + len(query)]
                match['after'] = match[field][i + len(query):]
                matched_fields.append((field, match))

        context = {
            'wines': wines,
            'query': query,
            'matched_fields': matched_fields
        }
        return render(request, 'autocomplete.html', context)
    else:
        return Http404


def checkout(request):
    if request.is_ajax() and request.GET:
        context = getCartContext(request)
        context['name'] = request.GET['name']
        context['email'] = request.GET['email']
        context['phone'] = request.GET['phone']
        context['address'] = request.GET['address']
        context['city'] = request.GET['city']
        context['state'] = request.GET['state']
        context['zipcode'] = request.GET['zipcode']
        context['comment'] = request.GET['comment']

        msg_text = render_to_string('email.txt', context)
        msg_html = render_to_string('email.html', context)

        sent = send_mail(
            subject='Order Inquiry from ' + request.GET['name'],
            message=msg_text,
            from_email='info@shyrwines.com',
            recipient_list=['sanjay@shyrwines.com'],
            html_message=msg_html
        )
        if sent:
            request.session.pop('cart')
            return HttpResponse('0', content_type='application/json')
        else:
            return HttpResponse('Error sending email.',
                content_type='application/json')
    else:
        raise Http404


def update(request):
    if request.is_ajax() and request.GET:
        quantity = int(request.GET['quantity'])
        if quantity:
            request.session['cart'][request.GET['id']] = quantity
        else:
            request.session['cart'].pop(request.GET['id'])
        request.session.modified = True
        return render(request, 'cart-items.html', getCartContext(request))
    else:
        raise Http404


def remove(request):
    if request.is_ajax() and request.GET:
        request.session['cart'].pop(request.GET['id'])
        request.session.modified = True
        return render(request, 'cart-items.html', getCartContext(request))
    else:
        raise Http404
