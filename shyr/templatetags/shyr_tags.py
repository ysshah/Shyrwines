from django import template


register = template.Library()


@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    dict_.pop('page', None)
    return dict_.urlencode()


@register.simple_tag
def url_page(request, page):
    dict_ = request.GET.copy()
    dict_['page'] = page
    return dict_.urlencode()


@register.simple_tag
def url_remove(request, field):
    dict_ = request.GET.copy()
    dict_.pop(field, None)
    dict_.pop('page', None)
    return dict_.urlencode()
