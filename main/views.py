import re
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request,'index.html')

def demo(request):
    return render(request,'demo.html')