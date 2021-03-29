from django.shortcuts import render
from app01.myforms import MyRegForm


# Create your views here.


def register(request):
    form_obj = MyRegForm()
    return render(request, 'register.html', locals())
