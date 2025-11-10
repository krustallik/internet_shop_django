from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('buy/<int:product_id>/', views.buy_now, name='buy_now'),
    path('success/<int:order_id>/', views.order_success, name='success'),
]
