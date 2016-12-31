import json
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.staticfiles import finders
from django.views.decorators.http import require_POST
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

filter_fields = (
    'country',
    'region',
    'appellation',
    'varietal'
)

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
        context['subtotal'] = subtotal
        context['tax'] = subtotal * 0.0875
        context['total'] = subtotal * 1.0875
    else:
        context['cart'] = None

    return context


def getAllWinesContext(request):
    filter_args = {}
    for field in filter_fields:
        if field in request.GET:
            filter_args[field] = request.GET[field]

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

    wines = Wine.objects.filter(**filter_args)

    choices = []
    for field in filter_fields:
        field_choices = list(wines.order_by(field).values_list(
            field, flat=True).distinct())
        if None in field_choices:
            field_choices.remove(None)
        if len(field_choices) == 1:
            filter_args[field] = field_choices[0]
        # else:
        #     field_choices.insert(0, 'Any')
        if filter_args.get(field) in field_choices:
            offset = (field_choices.index(filter_args[field]) + 1) * -51
        else:
            offset = 0
        choices.append((field, filter_args.get(field, 'Any'), field_choices, offset))

    if request.GET.get('price') in price_options:
        offset = (price_options.index(request.GET['price']) + 1) * -51
    else:
        offset = 0
    choices.append(('price', request.GET.get('price', 'Any'), price_options, offset))

    if request.GET.get('sort') in sort_options:
        offset = sort_options.index(request.GET['sort']) * -51
    else:
        offset = 0
    choices.append(('sort', request.GET.get('sort', sort_options[0]), sort_options, offset))

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
        'choices': choices
    }
    return context


def add(request):
    if request.is_ajax() and request.POST:
        if 'cart' in request.session:
            request.session['cart'][request.POST['id']] = request.session['cart'].get(
                request.POST['id'], 0) + int(request.POST['quantity'])
            request.session.modified = True
        else:
            request.session['cart'] = {
                request.POST['id']: int(request.POST['quantity'])
            }
        return HttpResponse('1', content_type='application/json')
    else:
        raise Http404


def autocomplete(request):
    if request.is_ajax() and request.GET:
        query = request.GET['q'].lower()
        wines = Wine.objects.filter(name__contains=query)
        for wine in wines:
            i = wine.name.lower().index(query)
            wine.before = wine.name[:i]
            wine.match = wine.name[i:i + len(query)]
            wine.after = wine.name[i + len(query):]

        matched_fields = []
        for field in filter_fields:
            for match in Wine.objects.values(field).distinct().filter(**{field+'__contains':query}):
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
    if request.is_ajax() and request.POST:
        quantity = int(request.POST['quantity'])
        if quantity:
            request.session['cart'][request.POST['id']] = quantity
        else:
            request.session['cart'].pop(request.POST['id'])
        request.session.modified = True
        return HttpResponse('1', content_type='application/json')
    else:
        raise Http404


def remove(request):
    if request.is_ajax() and request.POST:
        request.session['cart'].pop(request.POST['id'])
        request.session.modified = True
        return HttpResponse('1', content_type='application/json')
    else:
        raise Http404


def all_wines_items(request):
    if request.is_ajax():
        pass
    else:
        raise Http404


def cart_items(request):
    if request.is_ajax():
        return render(request, 'cart-items.html', getCartContext(request))
    else:
        raise Http404
