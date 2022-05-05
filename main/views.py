import re
import os
import asyncio
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import base64
import json
from django.conf import settings

from datetime import datetime
from main.utility import *
# Create your views here.


def index(request):
    return render(request, 'index.html')


async def process_backend(request):
    #if is_ajax(request=request) and request.method == "POST":
    if  request.method == "POST":
        # request.POST
        # request.POST.get('firstnamevalue')
        #vpu = request.POST.get('vpu')
        vpu = request.POST.get('vpu')
        fixmvasc = request.POST.get('fixmvasc')
        tab = request.POST.get('tab')
        percenz = request.POST.get('percenz')

        type = request.POST.get('type')
        length = request.POST.get('length')
        h01_kw = request.POST.get('h01_kw')
        h01_pf = request.POST.get('h01_pf')
        sg01pf = request.POST.get('sg01pf')

        h02_kw = request.POST.get('h02_kw')
        h02_pf = request.POST.get('h02_pf')
        sg02pf = request.POST.get('sg02pf')

        h03_kw = request.POST.get('h03_kw')
        h03_pf = request.POST.get('h03_pf')
        sg03pf = request.POST.get('sg03pf')

        batt_kw = request.POST.get('batt_kw')
        batt_pf = request.POST.get('batt_pf')
        sgBattPkw = request.POST.get('sgBattPkw')
        sgBattPF = request.POST.get('sgBattPF')

        evBattKw = request.POST.get('evBattKw')
        evBattPf = request.POST.get('evBattPf')
        sgEVBattPkw = request.POST.get('sgEVBattPkw')
        sgEVBattPF = request.POST.get('sgEVBattPF')

        print(list(request.POST.items()))

        postData = {
            "vpu": vpu,
            "fixmvasc": fixmvasc,

            "tab": tab,
            "percenz": percenz,
            "type": type,
            "length": length,
            "h01_kw": h01_kw,
            "h01_pf": h01_pf,
            "sg01pf": sg01pf,
            "h02_kw": h02_kw,
            "h02_pf": h02_pf,
            "sg02pf": sg02pf,
            "h03_kw": h03_kw,
            "h03_pf": h03_pf,
            "sg03pf": sg03pf,
            "batt_kw": batt_kw,
            "batt_pf": batt_pf,
            "sgBattPkw": sgBattPkw,
            "sgBattPF": sgBattPF,
            "evBattKw": evBattKw,
            "evBattPf": evBattPf,
            "sgEVBattPkw": sgEVBattPkw,
            "sgEVBattPF": sgEVBattPF,
        }
        
        loop = asyncio.get_running_loop()
        task1 = loop.create_task(callOpenDSS(postData,getTimestamp()))
        resultFile = await task1
        if task1.done():
            print('callOpenDSS task completed: {}'.format(task1.result()))
        else:
            print('task not completed after 5 seconds, aborting')
            task1.cancel() 

        #try:
        #    loop.run_until_complete(callOpenDSS(postData,getTimestamp()))
        #finally:
        #    loop.close()

        json_object = json.loads(resultFile)

        if(json_object["status"]=="success"):
                
            # read chart-image convert to hex-binary file and return to web-ui
            # get path
            image_path = getattr(settings, "CHART_PATH", None)
            #convert jpec to hex rawdata
            with open(image_path+json_object["filename"], "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
              # return result to json format
                return JsonResponse({"success": "test", "data": postData,"output_lv": json_object["output_lv"],"output_pcc": json_object["output_pcc"],"line": json_object["line"],"kilojoule": json_object["kilojoule"],"output_line": json_object["output_line"],  "fileName": json_object["filename"], "raw": image_data}, status=200)

        else:
                print("Problem in create DSS file.")
                # return result to json format
                return JsonResponse({"error": "Problem in create DSS file."}, status=400)
    else:
        return JsonResponse({"error": "bad-request-method"}, status=200)

def demo(request):
    return render(request, 'demo.html')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


async def calculate(data):
    print("this calculate data.")
    print(data)
    return JsonResponse({"success": "calculate()", "data": data}, status=200)

def process(request):
    
    if request.method == "POST":

        postData = {
            "vpu": request.POST.get('vpu'),
            "fixmvasc": request.POST.get('fixmvasc'),
            "tab": request.POST.get('tab'),
            "percenz": request.POST.get('percenz'),
            "type": request.POST.get('type'),
            "length": request.POST.get('length'),
            "h01_kw": request.POST.get('h01_kw'),
            "h01_pf": request.POST.get('h01_pf'),
            "sg01pf": request.POST.get('sg01pf'),
            "h02_kw": request.POST.get('h02_kw'),
            "h02_pf": request.POST.get('h02_pf'),
            "sg02pf": request.POST.get('sg02pf'),
            "h03_kw": request.POST.get('h03_kw'),
            "h03_pf": request.POST.get('h03_pf'),
            "sg03pf": request.POST.get('sg03pf'),
            "batt_kw": request.POST.get('batt_kw'),
            "batt_pf": request.POST.get('batt_pf'),
            "sgBattPkw": request.POST.get('sgBattPkw'),
            "sgBattPF": request.POST.get('sgBattPF'),
            "evBattKw": request.POST.get('evBattKw'),
            "evBattPf": request.POST.get('evBattPf'),
            "sgEVBattPkw": request.POST.get('sgEVBattPkw'),
            "sgEVBattPF": request.POST.get('sgEVBattPF'),
        }



        #loop = asyncio.get_running_loop()
        #task1 = loop.create_task(openDSSTicker3(postData,getTimestamp()))
        #resultFile = await task1
        #if task1.done():
        #    print('callOpenDSS task completed: {}'.format(task1.result()))
        #    #resultFile = await task1
        #    json_object = json.loads(task1.result())
        #    return JsonResponse({"success": "test", "data": postData,"output_lv": json_object["output_lv"],"output_pcc": json_object["output_pcc"],"line": json_object["line"],"kilojoule": json_object["kilojoule"],"output_line": json_object["output_line"],  "fileName": json_object["filename"], "raw": ''}, status=200)
        
        #else:
        #    print('task not completed after 5 seconds, aborting')
        #    task1.cancel() 
        #    return JsonResponse({"error": "process exception"}, status=200)
        resultFile = openDSSTicker(postData,getTimestamp())
        json_object = json.loads(resultFile)

        if(json_object["status"]=="success"):
                
            # read chart-image convert to hex-binary file and return to web-ui
            # get path
            image_path = getattr(settings, "CHART_PATH", None)
            #convert jpec to hex rawdata
            with open(image_path+json_object["filename"], "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
              # return result to json format
                return JsonResponse({"success": "test", "data": postData,"output_lv": json_object["output_lv"],"output_pcc": json_object["output_pcc"],"line": json_object["line"],"kilojoule": json_object["kilojoule"],"output_line": json_object["output_line"],  "fileName": json_object["filename"], "raw": image_data}, status=200)

        else:
                print("Problem in call open dss ")
                # return result to json format
                return JsonResponse({"error": "Problem in create DSS file."}, status=400)
        #return JsonResponse({"success": "test", "data": postData,"output_lv": json_object["output_lv"],"output_pcc": json_object["output_pcc"],"line": json_object["line"],"kilojoule": json_object["kilojoule"],"output_line": json_object["output_line"],  "fileName": json_object["filename"], "raw": ''}, status=200)
    
    else:
        return JsonResponse({"error": "bad-request-method"}, status=200)
    

