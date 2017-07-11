from django.shortcuts import render

# Create your views here.


def stu_index(request):
    return render(request, "student/stu_index.html")
