from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('query/', views.Query_Results , name='Query_Results'),
    path('transaction/', views.Add_Transaction, name='Add_Transaction'),
    path('stocks/', views.Buy_Stocks, name='Buy_Stocks'),
    path('transaction/input_Transaction', views.input_Transaction, name='input_Transaction'),
    path('stocks/input_stock', views.input_stock, name='input_stock'),

]