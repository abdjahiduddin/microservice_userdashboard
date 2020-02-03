from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    # path("analytic/<username>",views.analytic, name="analytic")
    path("arrhytmia",views.arrhytmia, name="analytic"),
    path("ecgnewdata",views.arrhytmia_process, name="analytic"),
    path("ecgshowdata",views.arrhytmia_history, name="analytic"),
    path("dashboard",views.heart_rate, name="analytic"),
    path("process",views.trend_process, name="analytic"),
    path("article_summary/<status>",views.article_summaries, name="analytic")
]
