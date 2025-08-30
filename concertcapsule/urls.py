"""
URL configuration for concertcapsule project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from concertcapsuleapi.views import ArtistView, VenueView, ConcertView, UserView, register_user, check_user
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'artists', ArtistView, 'artist')
router.register(r'venues', VenueView, 'venue')
router.register(r'concerts', ConcertView, 'concert')
router.register(r'users', UserView, 'user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', register_user),
    path('checkuser', check_user),
    path('', include(router.urls)),
    path('concerts/<int:pk>/', ConcertView.as_view({'delete': 'destroy'})),
]
