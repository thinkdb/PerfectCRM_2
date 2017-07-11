from django.conf.urls import url
from crm import views

urlpatterns = [
    url(r'^$', views.sales_index, name="sales_index"),
    url(r'customers/', views.customer_list, name="customer_list"),
]
