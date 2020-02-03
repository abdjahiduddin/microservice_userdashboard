from django.urls import path
from . import views
from django.contrib.auth.views import login_required

urlpatterns = [
    path('vtoken', views.validate_token, name='validate_token'),
    path('vtopic', views.validate_topic, name='validate_topic'),
    path('idname', views.get_id_name, name='validate_topic'),
    path('gettime', views.get_time, name='get_time'),
]
