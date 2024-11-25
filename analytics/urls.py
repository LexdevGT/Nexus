# analytics/urls.py
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/analyze-data/', views.analyze_data, name='analyze_data'),
]