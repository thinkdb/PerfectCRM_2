from django.shortcuts import render, HttpResponse

# Create your views here.


def sales_index(request):
    return render(request, "index.html")


def customer_list(request):
    return render(request, "sales/customers.html")