from django.conf.urls import url

from . import views

urlpatterns = [
    #url(r'^$', views.main, name='main'),
    url(r'^auth', views.auth, name='auth'),
    url(r'^cancel', views.cancel, name='cancel'),
    url(r'^index', views.index, name='index'),
    url(r'^home', views.home, name='home'),
    url(r'^login', views.login, name='login'),
    url(r'^verify', views.login_verify, name='login_verify'),
    url(r'^user', views.user, name='user'),
    url(r'^delete', views.delete, name='delete'),
    url(r'^create', views.create, name='create'),
    url(r'^forbidden', views.forbidden, name='forbidden'),
    url(r'^active_user', views.active_user, name='active_user'),
]
