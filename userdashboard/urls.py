from django.urls import path, include

from . import views
from accounts import views as views_accounts

urlpatterns = [
    path('', views.main, name='userdashboard' ),
    path('editprofile/', views_accounts.edit_profile, name='accountseditprofile' ),
    path('topic/', views.topic, name='topic' ),
    path('topic/create', views.topiccreate, name='topiccreate' ),
    path('topic/<topic_name>', views.topicdetail, name='topicdetail' ),
    path('topic/<topic_name>/update/', views.topicupdate, name='topicupdate' ),
    path('topic/<topic_name>/explorer/', views.topicexplorer,
        name='topicexplorer' ),
    path('topic/<topic_name>/delete/', views.topicdelete, name='topicdelete' ),
    path('topic/<topic_name>/<data_id>/', views.topicquery,
        name='topicquery' ),
    path('device/', views.device, name='device' ),
    path('device/create', views.devicecreate, name='devicecreate' ),
    path('device/<device_name>', views.devicedetail, name='devicedetail' ),
    path('device/<device_name>/update/', views.deviceupdate, name='deviceupdate' ),
    path('device/<device_name>/delete/', views.devicedelete, name='devicedelete' ),
    path('analytic/', views.analytic, name='analytic' ),
    path('analytic/work/', views.analyticwork, name='analyticwork' ),
    path('analytic/<topic_name>', views.analyticstatistics,
        name='analyticstatistics' ),
    path('analytic/<topic_name>/explorer/', views.topicexplorer,
        name='topicexplorer' ),
    path('analytic/<topic_name>/train/', views.analytictrain,
        name='analytictrain' ),
    path('analytic/<topic_name>/predict/', views.analyticpredict,
        name='analyticpredict' ),
    path('analytic/<topic_name>/classify/', views.analyticclassify,
        name='analyticclassify' ),
]
