from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.login, name='login' ),
    path('signup/', views.signup, name='signup' ),
    path('logout/', views.logout, name='logout' ),
    path('', include('django.contrib.auth.urls')),
    #path('<user_name>/', views.edit_profile,name='editprofile'),
    #path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),

]

