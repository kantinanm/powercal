import re
import os
import asyncio
from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
import win32com.client
#import dss
import pythoncom
#import opendssdirect as dss
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
        dss_file=json_output["filename"]
        timestamp=json_output["timestamp"]
        
        if(json_output["status"]):
            task2 = asyncio.create_task(callOpenDSS(postData,dss_file,timestamp))
            resultFile = await task2
            json_object = json.loads(resultFile)
                        
            # read chart-image convert to hex-binary file and return to web-ui
            # get path
            image_path = getattr(settings, "CHART_PATH", None)
            #convert jpec to hex rawdata
            with open(image_path+json_object["filename"], "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
              # return result to json format
            return JsonResponse({"success": "test", "data": postData,"output_lv": json_object["output_lv"],"output_pcc": json_object["output_pcc"],  "fileName": json_object["filename"], "raw": image_data}, status=200)

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


async def callOpenDSS(data,dss_file,timestamp):
    
    dss_path = getattr(settings, "DSS_PATH", None) #get path

    print("Process callOpenDSS")

    pythoncom.CoInitialize() 
    dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
    
    #try:
    #    pythoncom.CoInitialize() 
    #    DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")


    #except:
    #    print 
    #    "Unable to start the OpenDSS Engine"
    #raise SystemExit

    dssText = dssObj.Text
    dssText.Command = r"compile 'D:\Work\OpenDSS\TestOV2.dss"
    dssCircuit = dssObj.ActiveCircuit
    dssSolution = dssCircuit.Solution
    dssElem = dssCircuit.ActiveCktElement
    dssBus = dssCircuit.ActiveBus
    
    dict = {
        'posZero':data["vpu"],
        'pos01':data["tab"],
        'pos02':data["percenz"],
        'pos03':data["type"],
        'pos04':data["length"],
        'pos05':data["h01_kw"],
        'pos06':data["h01_pf"],#sg01pf
        'pos07':data["h02_kw"],
        'pos08':data["h02_pf"],#sg02pf
        'pos09':data["h03_kw"],
        'pos10':data["h03_pf"],#sg03pf
        'pos11':data["batt_kw"], #sgBattPkw
        'pos12':data["batt_pf"], #sgBattPF
        'pos13':data["evBattKw"], #sgEVBattPkw
        'pos14':data["evBattPf"], #sgEVBattPF
    }

    posZero=float(dict['posZero'])
    pos01=float(dict['pos01'])
    pos02=float(dict['pos02'])
    pos04=float(dict['pos04'])

    print(f'pos-Zero value is: {posZero}')
    print(f'pos-01 value is: {pos01}')
    print(f'pos-02 value is: {pos02}')


    print("ui value of type is "+dict['pos03'])
    
    if dict['pos03'] == "small" :
        code = "THW-A"
    elif dict['pos03'] == "large" :
        code = "NYY"
    print("type is "+code)


    dssCircuit.Vsources.pu = 1.03
    #dssCircuit.Vsources.pu = dict['posZero']
    #dssCircuit.Vsources.MVAsc3 = 500

    transName = "Transformer.TR01"
    dssCircuit.Transformers.Name = transName.split(".")[1]
    #dssCircuit.Transformers.tap = dict['pos01']
    #dssCircuit.Transformers.xhl = dict['pos02']
    dssCircuit.Transformers.tap = 1.00
    dssCircuit.Transformers.xhl = 11.7

    lineName = "Line.Feeder1"
    dssCircuit.Lines.Name = lineName.split(".")[1]
    #dssCircuit.Lines.linecode = "THW-A"
    dssCircuit.Lines.linecode = code
    #dssCircuit.Lines.length = dict['pos04']
    dssCircuit.Lines.length = 4

    loadName = "Load.H01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    #dssCircuit.Loads.kW = dict['pos06']
    #dssCircuit.Loads.pf = dict['pos05']
    dssCircuit.Loads.kW = 2.1
    dssCircuit.Loads.pf = 0.91

    loadName = "Load.H02"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    #dssCircuit.Loads.kW = dict['pos07']
    #dssCircuit.Loads.pf = dict['pos08']
    dssCircuit.Loads.kW = 2.2
    dssCircuit.Loads.pf = 0.92

    loadName = "Load.H03"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    #dssCircuit.Loads.kW = dict['pos09']
    #dssCircuit.Loads.pf = dict['pos10']
    dssCircuit.Loads.kW = 2.3
    dssCircuit.Loads.pf = 0.93

    loadName = "Load.EV01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    #dssCircuit.Loads.kW = dict['pos11'] #-
    #dssCircuit.Loads.pf = dict['pos12']
    dssCircuit.Loads.kW = 2.4
    dssCircuit.Loads.pf = -0.95

    loadName = "Load.PV01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    #dssCircuit.Loads.kW = dict['pos13'] #-
    #dssCircuit.Loads.pf = dict['pos14']
    dssCircuit.Loads.kW = -3.0
    dssCircuit.Loads.pf = 1.0

    dssSolution.Solve()

    #dssText.Command = "Show Powers [kVA] [Elements]"

    #dssText.Command = "Set normvminpu = 0.9"
    #dssText.Command = "Set normvmaxpu = 1.1"
    #dssText.Command = "Plot profile phases=all"

    voltages_csv_name='EXP_VOLTAGES_'+timestamp+'.CSV'
    power_csv_name='EXP_POWERS_'+timestamp+'.CSV'
    
    dssText.command = "Export Powers [kVA] ["+power_csv_name+"]"
    dssText.command = "Export Voltage ["+voltages_csv_name+"]"


    #dss_engine.ActiveCircuit.Solution.Solve()
    #voltages = dss_engine.ActiveCircuit.AllBusVolts

    #read result
    task2 = asyncio.create_task(readResult(voltages_csv_name))
    raw_output = await task2
    json_output = json.loads(raw_output)

    if(json_output["status"]):
        print("result is OK : back form Utility")
        print("You can see.")
        print(json_output["output_lv"])
        print(json_output["output_pcc"])


        data_lv=json_output["output_lv"]
        data_pcc=json_output["output_pcc"]
        
        ####### read excel to generate chart #######
    
        dir_name = getattr(settings, "CHART_PATH", None)
        #dir_name = "D:/Work/Git/Python/powercal/static/images/"

        plt.rcParams["savefig.directory"] = os.chdir(os.path.dirname(dir_name))

        verts = [
            (0.0, data_lv["V1"]),   # P0
            (pos04, data_pcc["V1"]),  # P1
            (0.0, data_lv["V2"]),  # P2
            (pos04, data_pcc["V2"]),  # P3
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
        ax.grid()

        xs, ys = zip(*verts)
        ax.plot(xs, ys, 'x--', lw=2, color='black', ms=10)

        #ax.set_aspect('auto')
        #ax.set_xlim(xmin=0.0, xmax=pos04)
        ax.set_ybound(lower=0.9, upper=1.1)
        ax.set_xbound(lower=0.0, upper=pos04)
        #ax.set_xlim(-0.1, 1.1)
        #ax.set_ylim(-0.1, 1.1)

        # plt.style.use('seaborn-whitegrid')
        #xpoints = np.array([0, 6])
        #ypoints = np.array([0, 250])

        ax.set_title('L-N Voltage Profile\n',
             fontsize = 14, fontweight ='bold')

        #plt.plot(xpoints, ypoints)
        # plt.show()
        now = datetime.now()  # current date and time
        date_time = now.strftime("%m%d%Y_%H%M%S")

        title = "chart_"+date_time
        #plt.xlabel("n iteration")
        #plt.legend(loc='upper left')
        # plt.title(title)

        plt.xlabel("Distance(km)")
        #plt.ylabel("Gold")


        plt.savefig(title+".png", dpi=150)  # should before plt.show method
        plt.close()
        # plt.show()
        
        #success
        result = {'status':'success','filename': title+".png",'csv_file': voltages_csv_name,'output_lv':data_lv,'output_pcc':data_pcc}

    else:
        #fail to process
        result = {'status':'fail','filename': title+".png",'csv_file': voltages_csv_name}


    await asyncio.sleep(3)

    print("this call OpenDSS Engine.")
    print(data)
    return json.dumps(result)

