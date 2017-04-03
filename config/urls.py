"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from config import settings
from product import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.product_list, name="home"),
    url(r'^products/$', views.product_list, name="product"),
    url(r'^products/(?P<slug>\w+)/$', views.product_detail, name="one_product"),
    url(r'^product_vote/(?P<pk>\d+)/(?P<slug>\w+)/', views.product_vote, name="product_vote"),
    url(r'^signup/', views.signup, name="signup"),
    url(r'^login/', auth_views.login, {'template_name': 'login.html'}, name="login"),
    url(r'^logout/', auth_views.logout, {'next_page': '/login/'}, name="logout"),
    url(r'^comment_add/', views.comment_add, name="comment_add"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
