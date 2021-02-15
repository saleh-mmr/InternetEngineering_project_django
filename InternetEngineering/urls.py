"""InternetEngineering URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from myapp.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', signup, name='signup'),
    url(r'^login/', login, name='login'),
    url(r'^logout/', logout, name='logout'),
    url(r'^user-info/', get_user_info, name='userInfo'),
    url(r'^new-trip/', add_trip, name='newTrip'),
    url(r'^add-participant/(?P<pk>\d+)$', add_participant, name='addParticipant'),
    url(r'^check-participant/', check_participant, name='checkParticipant'),
    url(r'^user-all-trips/', get_user_trips, name='userAllTrips'),
    url(r'^trip-info/(?P<pk>\d+)$', get_trip_info, name='tripInfo'),
    url(r'^trip-participants/(?P<pk>\d+)$', get_trip_participant, name='tripParticipants'),
    url(r'^trip-transactions/(?P<pk>\d+)$', get_trip_transactions, name='tripTransactions'),
    url(r'^edit-trip-info/(?P<pk>\d+)$', edit_trip_info, name='editTripInfo'),
    url(r'^add-transaction/', add_transaction, name='newTransaction'),
    url(r'^calculate-dong/(?P<pk>\d+)$', calculate_dong, name='calculateDong'),

]
