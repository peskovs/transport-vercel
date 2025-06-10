# transport/urls.py
from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    # Sākumlapa
    path('', views.home, name='home'),
    path('routes/save_favorite/', views.save_favorite_route, name='save_favorite_route'),
    path('routes/remove_favorite/', views.remove_favorite_route, name='remove_favorite_route'),

    # Maršruti
    path('routes/', views.routes_list, name='routes_list'),
    path('routes/<int:route_id>/', views.route_details, name='route_details'),
    path('routes/<int:route_id>/atsauksme/', views.submit_atsauksme, name='submit_atsauksme'),
    path('atsauksme/<int:atsauksme_id>/delete/', views.delete_atsauksme, name='delete_atsauksme'),

    # Pieturas
    path('stops/', views.stops_list, name='stops_list'),
    path('stops/<int:stop_id>/', views.stop_details, name='stop_details'),

    # Satiksme
    path('traffic/', views.traffic_information, name='traffic_information'),
    path('traffic/report/', views.report_traffic, name='report_traffic'),

    # Statistika
    path('statistics/', views.statistics, name='statistics'),

    # Operatora panelis
    path('operator/dashboard/', views.operator_dashboard, name='operator_dashboard'),

    # Administratora panelis
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]