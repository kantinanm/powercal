import re
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers


# Create your views here.
def index(request):
    return render(request,'index.html')

def process_backend(request):
    if is_ajax(request=request) and request.method == "POST":
        #request.POST
        #request.POST.get('firstnamevalue')

        return JsonResponse({"success": "test"}, status=200)
    return JsonResponse({"error": "error-msg"}, status=400)

def demo(request):
    return render(request,'demo.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'