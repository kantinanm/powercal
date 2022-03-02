import re
import asyncio
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers


# Create your views here.
def index(request):
    return render(request,'index.html')

async def process_backend(request):
    if is_ajax(request=request) and request.method == "POST":
        #request.POST
        #request.POST.get('firstnamevalue')
        vpu=request.POST.get('vpu')
        vpu=request.POST.get('vpu')
        fixmvasc=request.POST.get('fixmvasc')
        tab=request.POST.get('tab')
        percenz=request.POST.get('percenz')

        type=request.POST.get('type')
        length=request.POST.get('length')
        h01_kw=request.POST.get('h01_kw')
        h01_pf=request.POST.get('h01_pf')
        sg01pf=request.POST.get('sg01pf')

        h02_kw=request.POST.get('h02_kw')
        h02_pf=request.POST.get('h02_pf')
        sg02pf=request.POST.get('sg02pf')

        h03_kw=request.POST.get('h03_kw')
        h03_pf=request.POST.get('h03_pf')
        sg03pf=request.POST.get('sg03pf')

        batt_kw=request.POST.get('batt_kw')
        batt_pf=request.POST.get('batt_pf')
        sgBattPkw=request.POST.get('sgBattPkw')
        sgBattPF=request.POST.get('sgBattPF')

        evBattKw=request.POST.get('evBattKw')
        evBattPf=request.POST.get('evBattPf')
        sgEVBattPkw=request.POST.get('sgEVBattPkw')
        sgEVBattPF=request.POST.get('sgEVBattPF')

        print(list(request.POST.items()))

        postData={
            "vpu":vpu,
            "fixmvasc":fixmvasc,
            
            "tab":tab,
            "percenz":percenz,
            "type":type,
            "length":length,
            "h01_kw":h01_kw,
            "h01_pf":h01_pf,
            "sg01pf":sg01pf,
            "h02_kw":h02_kw,
            "h02_pf":h02_pf,
            "sg02pf":sg02pf,
            "h03_kw":h03_kw,
            "h03_pf":h03_pf,
            "sg03pf":sg03pf,
            "batt_kw":batt_kw,
            "batt_pf":batt_pf,
            "sgBattPkw":sgBattPkw,
            "sgBattPF":sgBattPF,
            "evBattKw":evBattKw,
            "evBattPf":evBattPf,
            "sgEVBattPkw":sgEVBattPkw,
            "sgEVBattPF":sgEVBattPF,
        }

        await calculate(postData)
        task1 =asyncio.create_task(calculate(postData))

        resultFile= await task1
        #return result to json format
        #print fileName


        return JsonResponse({"success": "test","data":postData}, status=200)
    return JsonResponse({"error": "error-msg"}, status=400)

def demo(request):
    return render(request,'demo.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

async def calculate(data):
    print("this calculate data.")
    print(data)
    return JsonResponse({"success": "calculate()","data":data}, status=200)

async def callOpenDSS(data):
    print("this call OpenDSS Engine.")
    print(data)