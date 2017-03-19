from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^$', views.contact, name='contact'),
	url(r'^reminder/$', views.reminder, name='reminder'),
	url(r'^update/$', views.update, name='update')
]