from django.conf.urls import url
from . import views, ajax

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^all-wines/$', views.all_wines, name='all-wines'),
    url(r'^cart/$', views.cart, name='cart'),
    url(r'^contact-us/$', views.contact_us, name='contact-us'),
    url(r'^privacy-policy/$', views.privacy_policy, name='privacy-policy'),
    url(r'^terms-of-service/$', views.terms_of_service, name='terms-of-service'),
    url(r'^view/(?P<wine_id>\d+)/$', views.view, name='view'),

    url(r'^cart-items/$', ajax.cart_items, name='cart-items'),

    url(r'^add/$', ajax.add, name='add'),
    url(r'^autocomplete/$', ajax.autocomplete, name='autocomplete'),
    url(r'^checkout/$', ajax.checkout, name='checkout'),
    url(r'^update/$', ajax.update, name='update'),
    url(r'^remove/$', ajax.remove, name='remove')
]
