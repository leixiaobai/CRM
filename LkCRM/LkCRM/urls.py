"""LkCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from Crm import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('get_vaildcode_img/', views.get_vaildcode_img, name='get_vaildcode_img'),
    # path('register/', views.reg_modelform, name='register'),
    path('register/', views.register, name='register'),
    path('index/', views.index, name='index'),

    re_path('^crm/', include("Crm.urls")),

    re_path(r'^rbac/', include('rbac.urls', namespace='rbac')),
]
