#from django.conf.urls import patterns, url
from django.conf.urls import url
from django.urls import path

#from django.contrib.auth.views import login, logout
from django.contrib.auth import views as auth_views
from pydash.views import index, uptime, memusage, cpuusage, getdisk, \
getusers, getips, gettraffic, getproc, getdiskio, loadaverage, platform, \
getcpus, getnetstat

urlpatterns = [
       url(r'^$', index, name='index'),
       #url(r'login/$', auth_views.LoginView.as_view(template_name='login.html'),
       #    name='login'),
       #url(r'logout/$', auth_views.LoginView.as_view(template_name='logout.html'),
       #    name='logout'),
       #path('logout/', views.logout, name='logout' ),
       url(r'info/uptime/$', uptime, name='uptime'),
       url(r'info/memory/$', memusage, name='memusage'),
       url(r'info/cpuusage/$', cpuusage, name='cpuusage'),
       url(r'info/getdisk/$', getdisk, name='getdisk'),
       url(r'info/getusers/$', getusers, name='getusers'),
       url(r'info/getips/$', getips, name='getips'),
       url(r'info/gettraffic/$', gettraffic, name='gettraffic'),
       url(r'info/proc/$', getproc, name='getproc'),
       url(r'info/getdiskio/$', getdiskio, name='getdiskio'),
       url(r'info/loadaverage/$', loadaverage, name='loadaverage'),
       url(r'info/platform/([\w\-\.]+)/$', platform, name='platform'),
       url(r'info/getcpus/([\w\-\.]+)/$', getcpus, name='getcpus'),
       url(r'info/getnetstat/$', getnetstat, name='getnetstat')
]
