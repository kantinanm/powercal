import re
import os
import asyncio
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import win32com.client
import dss
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ColorConverter
import matplotlib.path as mpath
import matplotlib.text as text
import matplotlib.patches as patches
import numpy as np
import json
from django.conf import settings
import base64
from datetime import datetime
from main.utility import *
# Create your views here.


def index(request):
    return render(request, 'index.html')


async def process_backend(request):
    if is_ajax(request=request) and request.method == "POST":
        # request.POST
        # request.POST.get('firstnamevalue')
        vpu = request.POST.get('vpu')
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

        dss_path = getattr(settings, "DSS_PATH", None) #get path
        # await calculate(postData)
        # writeDSSFile(data)
        task1 = asyncio.create_task(writeDSSFile(postData,dss_path))
        raw_output = await task1
        json_output = json.loads(raw_output)

        print('DSS File '+json_output["filename"])
        
        if(json_output["status"]):
            task2 = asyncio.create_task(callOpenDSS(postData))
            resultFile = await task2
            json_object = json.loads(resultFile)
            # get path
            image_path = getattr(settings, "CHART_PATH", None)
            #convert jpec to hex rawdata
            with open(image_path+json_object["filename"], "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
              # return result to json format
            return JsonResponse({"success": "test", "data": postData, "fileName": json_object["filename"], "raw": image_data}, status=200)

        else:
            print("Problem in create DSS file.")
              # return result to json format
            return JsonResponse({"error": "Problem in create DSS file."}, status=400)

    return JsonResponse({"error": "bad-request-method"}, status=200)

def demo(request):
    return render(request, 'demo.html')


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


async def calculate(data):
    print("this calculate data.")
    print(data)
    return JsonResponse({"success": "calculate()", "data": data}, status=200)


async def callOpenDSS(data):
    #dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
    #dss_engine = dss.DSS
    #dss_engine.Text.Command = "compile d:/Work/OpenDSS/TestOV2.dss"


    
    
    dir_name = getattr(settings, "CHART_PATH", None)
    #dir_name = "D:/Work/Git/Python/powercal/static/images/"

    plt.rcParams["savefig.directory"] = os.chdir(os.path.dirname(dir_name))

    verts = [
        (0., 1.0297),   # P0
        (3., 1.0184),  # P1
        (0., 1.0286),  # P2
        (3., 0.9949),  # P3
    ]

    codes = [
        mpath.Path.MOVETO,
        mpath.Path.MOVETO,
        mpath.Path.MOVETO,
        mpath.Path.MOVETO,
    ]

    path = mpath.Path(verts, codes)

    fig, ax = plt.subplots()
    patch = patches.PathPatch(path, facecolor='none', lw=2)
    ax.add_patch(patch)

    xs, ys = zip(*verts)
    ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)

    #ax.set_xlim(-0.1, 1.1)
    #ax.set_ylim(-0.1, 1.1)

    # plt.style.use('seaborn-whitegrid')
    #xpoints = np.array([0, 6])
    #ypoints = np.array([0, 250])

    #plt.plot(xpoints, ypoints)
    # plt.show()
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m%d%Y_%H%M%S")

    title = "chart_"+date_time
    #plt.xlabel("n iteration")
    #plt.legend(loc='upper left')
    # plt.title(title)
    plt.savefig(title+".png", dpi=150)  # should before plt.show method
    plt.close()
    # plt.show()

    result = {'filename': title+".png"}
    await asyncio.sleep(3)

    print("this call OpenDSS Engine.")
    print(data)
    return json.dumps(result)

