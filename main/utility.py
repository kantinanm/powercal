from datetime import datetime
import asyncio
import json
#from turtle import end_fill
import csv
import pandas as pd
from django.conf import settings
import time
#import csv as csv
import win32com.client
#import dss
import pythoncom
#import py_dss_interface
#import opendssdirect as dss
import matplotlib
matplotlib.use('Agg') #WebAgg
import matplotlib.pyplot as plt
plt.switch_backend('Agg') 

#from matplotlib.collections import LineCollection
#from matplotlib.colors import ColorConverter
import matplotlib.path as mpath
#import matplotlib.text as text
import matplotlib.patches as patches

import numpy as np
#import base64
import os
#from io import BytesIO

async def writeDSSFile(data,path):
    print("this process for write DSS file.")

    now = datetime.now()  # current date and time
    date_time = now.strftime("%m%d%Y_%H%M%S")
    fileName = "solve_"+date_time+".dss"
    print(type(data))
    print(path)

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
    #print(dict)
    lines = [
        'ClearAll',
        'Set DefaultBaseFrequency=50',
        'New circuit.example basekV=22 pu='+dict['posZero']+' angle=0 frequency=50 phase=3 MVAsc3=500',
        'New Transformer.TR01 phases=3 windings=2 buses=(Sourcebus, LV) conns=(Delta wye) kvs=(22, 0.4) kvas=(250, 250) tap='+dict['pos01']+' xhl='+dict['pos02'],
        'New Linecode.THW-A  nphases=3 R1=0.3209 X1=0.2347 R0=0.9 X0=0.7 units=km',
        'New Linecode.NYY  nphases=3 R1=0.15 X1=0.08 R0=0.3 X0=0.24 units=km',
        'New Line.Feeder1 bus1=LV bus2=PCC length='+dict['pos04']+' linecode='+dict['pos03'],
        'New Load.H01 bus1=PCC.1 phases=1 Model=1 kV=0.23 kW='+dict['pos05']+' pf='+dict['pos06'],
        'New Load.H02 bus1=PCC.2 phases=1 Model=1 kV=0.23 kW='+dict['pos07']+' pf='+dict['pos08'],
        'New Load.H03 bus1=PCC.3 phases=1 Model=1 kV=0.23 kW='+dict['pos09']+' pf='+dict['pos10'],
        'New Load.EV01 bus1=PCC.1 phases=1 Model=1 kV=0.23 kW='+dict['pos11']+' pf='+dict['pos12'],
        'New Load.PV01 bus1=PCC.1 phases=1 Model=1 kV=0.23 kW='+dict['pos13']+' pf='+dict['pos14'],
        '!Monitor',
        '!New EnergyMeter.Feeder1  Element=Line.Feeder1 Terminal=1',
        'New EnergyMeter.TR1  Element=Transformer.TR01 Terminal=1',
        'Set voltagebases=(22, 0.4)',
        'Set algorithm=Newton',
        'Calcvoltagebases',
        '!Solve',
        '!Set normvminpu = 0.9',
        '!Set normvmaxpu = 1.1',
        '!Plot profile phases=all thickness = 10 label=y',
        '!Export Profile phases=all',
        '!Export Powers [kVA]',
        '!Export Voltages',
        '!Show Voltages [LN] [Elements]',
        'Show Powers [kVA] [Elements]',
        '!SetBusXY Bus = Sourcebus X=0 Y=100',
        '!SetBusXY Bus = LV X=200 Y=100',
        '!SetBusXY Bus = PCC X=600 Y=100',
        '!ClearBusMarkers',
        '!AddBusMarker Bus=LV code=16 color=Red size=30',
        '!AddBusMarker Bus=PCC code=16 color=Red size=30',
        '!Plot circuit label=y',
        ]

    with open(path+fileName, 'w', encoding='utf-8') as f:
        f.writelines('\n'.join(lines))

    print(fileName+"File has been created.")
    result = {'status': True,'filename':fileName,'timestamp':date_time}
    return json.dumps(result)
async def readResultPphase(p_phases_file):
    print("this process for read data from "+p_phases_file+" file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    df = pd.read_csv(
        path+p_phases_file,
        nrows=7, delimiter = ",",
        low_memory = True
    )
    #df['Bus'] = df['Bus'].astype(str)
    #df['pu1'] = df['pu1'].astype(float)
    #df['pu2'] = df['pu2'].astype(float)
    #df['pu3'] = df['pu3'].astype(float)

    print('Method 2: Starting Experiment')
    # timer starts
    start = time.time()
    # display information
    print('Show Infos:')
    df.info()
    print('')
    print('Show Top Seven Rows')
    print(df.head(7))

    kw1=df.iloc[0,3]
    kw2=df.iloc[0,5]
    kw3=df.iloc[0,7]

    pv1_joule=df.iloc[0,4]
    pv2_joule=df.iloc[0,6]
    pv3_joule=df.iloc[0,8]

    print(f'Line PV1 : {kw1},{pv1_joule}')
    print(f'Line PV2 : {kw2},{pv2_joule}')
    print(f'Line PV3 : {kw3},{pv3_joule}')


    line = {'PV1': abs(kw1), 'PV2': abs(kw2), 'PV3': abs(kw3)}
    kilojoule  = {'PV1': abs(pv1_joule), 'PV2': abs(pv2_joule), 'PV3': abs(pv3_joule)}
    output_line = {'PV1': str(abs(kw1))+", "+str(abs(pv1_joule))+" joule", 'PV2': str(abs(kw2))+", "+str(abs(pv2_joule))+" joule", 'PV3': str(abs(kw3))+", "+str(abs(pv3_joule))+" joule"}
    #output_line={}
    # timer ends
    end = time.time()
    print('\nExperiment Completed\nTotal Time: {:.2f} seconds'.format(end-start))

    result = {'status': True,'line':line,'kilojoule':kilojoule,'output_line':output_line}
    return json.dumps(result)
async def readResult(exp_voltages_file):
    
    print("this process for read data from "+exp_voltages_file+" file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    df = pd.read_csv(
        path+exp_voltages_file,
        nrows=4, delimiter = ",",
        low_memory = True
    )

    #df['Bus'] = df['Bus'].astype(str)
    #df['pu1'] = df['pu1'].astype(float)
    #df['pu2'] = df['pu2'].astype(float)
    #df['pu3'] = df['pu3'].astype(float)

    print('Method 2: Starting Experiment')
    # timer starts
    start = time.time()
    # display information
    print('Show Infos:')
    df.info()
    print('')
    print('Show Top Three Rows')
    print(df.head(3))


    lv_lv1_pu=df.iloc[1,5]
    lv_lv2_pu=df.iloc[1,9]
    lv_lv3_pu=df.iloc[1,13]

    pcc_v1_pu=df.iloc[2,5]
    pcc_v2_pu=df.iloc[2,9]
    pcc_v3_pu=df.iloc[2,13]

    print(f'LV: V1(pu) : {lv_lv1_pu}')
    print(f'LV: V2(pu) : {lv_lv2_pu}')
    print(f'LV: V3(pu) : {lv_lv3_pu}')

    print(f'PCC: V1(pu) : {pcc_v1_pu}')
    print(f'PCC: V2(pu) : {pcc_v2_pu}')
    print(f'PCC: V3(pu) : {pcc_v3_pu}')

    lv = {'V1': lv_lv1_pu, 'V2': lv_lv2_pu, 'V3': lv_lv3_pu}
    pcc = {'V1': pcc_v1_pu, 'V2': pcc_v2_pu, 'V3': pcc_v3_pu}

    # timer ends
    end = time.time()
    print('\nExperiment Completed\nTotal Time: {:.2f} seconds'.format(end-start))

    result = {'status': True,'output_lv':lv,'output_pcc':pcc}
    return json.dumps(result)

async def createChart(data_lv,data_pcc,length,timestamp):
    print("this call createChart.")
    dir_name = getattr(settings, "CHART_PATH", None)
    #dir_name = "D:/Work/Git/Python/powercal/static/images/"

    plt.rcParams["savefig.directory"] = os.chdir(os.path.dirname(dir_name))

    verts = [
            (0.0, data_lv["V1"]),   # P0
            (length, data_pcc["V1"]),  # P1
            (0.0, data_lv["V2"]),  # P2
            (length, data_pcc["V2"]),  # P3
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
    ax.set_xbound(lower=0.0, upper=length)
    #ax.set_xlim(-0.1, 1.1)
    #ax.set_ylim(-0.1, 1.1)

    #plt.style.use('seaborn-whitegrid')
    #xpoints = np.array([0, 6])
    #ypoints = np.array([0, 250])

    ax.set_title('L-N Voltage Profile\n',
    fontsize = 14, fontweight ='bold')

    #plt.plot(xpoints, ypoints)
    # plt.show()


    title = "chart_"+timestamp
    #plt.xlabel("n iteration")
    #plt.legend(loc='upper left')
    #plt.title(title)

    plt.xlabel("Distance(km)")
    #plt.ylabel("Gold")

    #buffer = BytesIO()
    plt.savefig( title+".png", dpi=150)  # should before plt.show method
    #plt.savefig(buffer, title+".png", dpi=150) 
    #buffer.seek(0)
    #image_png = buffer.getvalue()
    #buffer.close()
    #graphic = base64.b64encode(image_png)
    #graphic = graphic.decode('utf-8')

    plt.close()
    result = {'status':'success','filename': title+".png"}

    return json.dumps(result)

def mapSign(value,sign):
    if (sign=="neg") :
        return '-' +value
    else :
        return value
def getTimestamp():
    now = datetime.now()  # current date and time
    date_time = now.strftime("%m%d%Y_%H%M%S")
    return date_time
async def openDSSTickerDemo(data):
    print(data)
    result = {"status": "success", "filename": "chart_05032022_093829.png", "voltages_csv_file": "EXP_VOLTAGES_05032022_093829.CSV", "p_byPhase_csv_file": "EXP_P_ByPhase_05032022_093829.CSV", "output_lv": {"V1": 1.0296, "V2": 1.0285, "V3": 1.0284}, "output_pcc": {"V1": 1.0127, "V2": 0.94672, "V3": 0.9401}, "line": {"PV1": 1.521, "PV2": 2.391, "PV3": 2.445}, "kilojoule": {"PV1": 0.207, "PV2": 1.009, "PV3": 1.071}, "output_line": {"PV1": "1.521, 0.207 joule", "PV2": "2.391, 1.009 joule", "PV3": "2.445, 1.071 joule"}}
    return json.dumps(result)

def openDSSTicker(data,timestamp):
    print(data)
    print("Process openDSSTicker")

    PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
    print("Root path : "+PROJECT_PATH)
    dss_path = getattr(settings, "DSS_PATH", PROJECT_PATH+"dss") #get path
    dss_file = getattr(settings, "DSS_FILENAME", "engine.dss") #get filename

    pythoncom.CoInitialize() 
    dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
    #DSSStart = dssObj.Start("0")
    #if DSSStart:
    #    print("OpenDSS Engine started successfully")
    #else:
    #    print("Unable to start the OpenDSS Engine")
    
    #try:
    #    pythoncom.CoInitialize() 
    #    DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")


    #except:
    #    print 
    #    "Unable to start the OpenDSS Engine"
    #raise SystemExit

    dssText = dssObj.Text
    dssText.Command = "compile "+dss_path+dss_file
    dssCircuit = dssObj.ActiveCircuit
    dssSolution = dssCircuit.Solution
    dssElem = dssCircuit.ActiveCktElement
    dssBus = dssCircuit.ActiveBus
    #DSSCtrlQueue=dssCircuit.CtrlQueue
    DSSStart = dssObj.Start(0)

    if DSSStart:
        print("OpenDSS Engine started successfully")
    else:
        print("Unable to start the OpenDSS Engine")
    
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
        'pos11':data["evBattKw"], #sgEVBattPkw
        'pos12':data["evBattPf"], #sgEVBattPF
        'pos13':data["batt_kw"], #sgBattPkw
        'pos14':data["batt_pf"], #sgBattPF
    }

    posZero=float(dict['posZero'])
    pos01=float(dict['pos01'])
    pos02=float(dict['pos02'])
    pos04=float(dict['pos04'])
    pos05=float(mapSign(dict['pos06'],data["sg01pf"]))
    pos06=float(dict['pos05'])
    pos07=float(dict['pos07'])
    pos08=float(mapSign(dict['pos08'],data["sg02pf"]))
    pos09=float(dict['pos09'])
    pos10=float(mapSign(dict['pos10'],data["sg03pf"]))
    pos11=float(mapSign(dict['pos11'],data["sgEVBattPkw"]))
    pos12=float(mapSign(dict['pos12'],data["sgEVBattPF"]))
    pos13=float(mapSign(dict['pos13'],data["sgBattPkw"]))
    pos14=float(mapSign(dict['pos14'],data["sgBattPF"]))
    #posZero = 1.03
    #pos01 = 1.00
    #pos02 = 11.7
    #pos04 = 4
    #pos05 = 0.91
    #pos06 = 2.1
    #pos07 = 2.2
    #pos08 = 0.92
    #pos09 = 2.3
    #pos10 = 0.93
    #pos11 = 2.4
    #pos12 = -0.95
    #pos13 =-3.0
    #pos14 =1.0
    #debug
    print(f'pos-Zero value is: {posZero}')
    print(f'pos-01 value is: {pos01}')
    print(f'pos-02 value is: {pos02}')
    print(f'pos-04 value is: {pos04}')
    print(f'pos-05 value is: {pos05}')
    print(f'pos-06 value is: {pos06}')
    print(f'pos-07 value is: {pos07}')
    print(f'pos-08 value is: {pos08}')
    print(f'pos-09 value is: {pos09}')
    print(f'pos-10 value is: {pos10}')
    print(f'pos-11 value is: {pos11}')
    print(f'pos-12 value is: {pos12}')
    print(f'pos-13 value is: {pos13}')
    print(f'pos-14 value is: {pos14}')

    print("UI value of type is "+dict['pos03'])
    
    if dict['pos03'] == "small" :
        code = "THW-A"
    elif dict['pos03'] == "large" :
        code = "NYY"
    print("type is "+code)


    #dssCircuit.Vsources.pu = 1.03
    dssCircuit.Vsources.pu = posZero
    #dssCircuit.Vsources.MVAsc3 = 500

    transName = "Transformer.TR01"
    dssCircuit.Transformers.Name = transName.split(".")[1]
    dssCircuit.Transformers.tap = pos01
    dssCircuit.Transformers.xhl = pos02
    #dssCircuit.Transformers.tap = 1.00
    #dssCircuit.Transformers.xhl = 11.7

    lineName = "Line.Feeder1"
    dssCircuit.Lines.Name = lineName.split(".")[1]
    #dssCircuit.Lines.linecode = "THW-A"
    dssCircuit.Lines.linecode = code
    dssCircuit.Lines.length = pos04
    #dssCircuit.Lines.length = 4

    loadName = "Load.H01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    dssCircuit.Loads.kW = pos06
    dssCircuit.Loads.pf = pos05
    #dssCircuit.Loads.kW = 2.1
    #dssCircuit.Loads.pf = 0.91

    loadName = "Load.H02"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    dssCircuit.Loads.kW = pos07
    dssCircuit.Loads.pf = pos08
    #dssCircuit.Loads.kW = 2.2
    #dssCircuit.Loads.pf = 0.92

    loadName = "Load.H03"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    dssCircuit.Loads.kW = pos09
    dssCircuit.Loads.pf = pos10
    #dssCircuit.Loads.kW = 2.3
    #dssCircuit.Loads.pf = 0.93

    loadName = "Load.EV01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    dssCircuit.Loads.kW = pos11 #-
    dssCircuit.Loads.pf = pos12
    #dssCircuit.Loads.kW = 2.4
    #dssCircuit.Loads.pf = -0.95

    loadName = "Load.PV01"
    dssCircuit.Loads.Name = loadName.split(".")[1]
    dssCircuit.Loads.kW = pos13 #-
    dssCircuit.Loads.pf = pos14
    #dssCircuit.Loads.kW = -3.0
    #dssCircuit.Loads.pf = 1.0


    #dssText.Command = "Show Powers [kVA] [Elements]"

    #dssText.Command = "Set normvminpu = 0.9"
    #dssText.Command = "Set normvmaxpu = 1.1"
    #dssText.Command = "Plot profile phases=all"


    dssSolution.Solve()


    voltages_csv_name='EXP_VOLTAGES_'+timestamp+'.CSV'
    power_csv_name='EXP_POWERS_'+timestamp+'.CSV'
    p_byPhases_csv_name='EXP_P_ByPhase_'+timestamp+'.CSV'
    losses_csv_name='losses_'+timestamp+'.CSV'
    
    dssText.command = "Export Powers [kVA] ["+power_csv_name+"]"
    dssText.command = "Export Voltage ["+voltages_csv_name+"]"
    dssText.command = "Export P_ByPhase [kVA] ["+p_byPhases_csv_name+"]"
    dssText.command = "Export Losses ["+losses_csv_name+"]"


    print("GetInterfaceCount()")
    print(pythoncom._GetInterfaceCount())
    pythoncom.CoFreeUnusedLibraries()
    pythoncom.CoUninitialize()


    #read result
    #readResultVoltages
    raw_output =readResultVoltages(voltages_csv_name)
    json_output = json.loads(raw_output)

    if(json_output["status"]):
        print("result is OK : back form Utility")
        print("You can see.")
        print(json_output["output_lv"])
        print(json_output["output_pcc"])

        data_lv=json_output["output_lv"]
        data_pcc=json_output["output_pcc"]

        #read result
        result =readResultpByPhase(p_byPhases_csv_name)
        resultByPhase = json.loads(result)

        line=[]
        kilojoule=[]
        output_line=[]
            
        if(resultByPhase["status"]):
            print("result is OK : back form readResultpByPhase() ,Utility")
            print("You can see.")
            print(resultByPhase["line"])
            print(resultByPhase["kilojoule"])
            print(resultByPhase["output_line"])

            line=resultByPhase["line"]
            kilojoule=resultByPhase["kilojoule"]
            output_line=resultByPhase["output_line"]

            resultLosses =readResultLosses(losses_csv_name)
            lossesData = json.loads(resultLosses)

            if(lossesData["status"]):
                output_losses=lossesData["output_losses"]
                output_pq=lossesData["output_pq"]
                print("result is OK : back form readResultLosses() ,Utility")
                print("You can see.")
                print(lossesData["output_losses"])
                print(lossesData["output_pq"])


                ####### read excel to generate chart #######
                raw_json = generateChart(data_lv,data_pcc,pos04,timestamp)
                chart_output_json = json.loads(raw_json)
                
                chartFileName=chart_output_json["filename"]

                if(chart_output_json["status"]=="success"):
                    print("generate chart completed.")
                else:
                    print("error to generate chart.!")
        
                result = {"status": "success", "filename": chartFileName, "voltages_csv_file": voltages_csv_name, "p_byPhase_csv_file": p_byPhases_csv_name, "output_lv": data_lv, "output_pcc": data_pcc, "line": line, "kilojoule": kilojoule, "output_line": output_line,"losses": output_losses,"output_pq": output_pq}

    else:
        result = {"status": "read fail"}
    #mock
    #result = {"status": "success", "filename": "chart_05032022_093829.png", "voltages_csv_file": "EXP_VOLTAGES_05032022_093829.CSV", "p_byPhase_csv_file": "EXP_P_ByPhase_05032022_093829.CSV", "output_lv": {"V1": 1.0296, "V2": 1.0285, "V3": 1.0284}, "output_pcc": {"V1": 1.0127, "V2": 0.94672, "V3": 0.9401}, "line": {"PV1": 1.521, "PV2": 2.391, "PV3": 2.445}, "kilojoule": {"PV1": 0.207, "PV2": 1.009, "PV3": 1.071}, "output_line": {"PV1": "1.521, 0.207 joule", "PV2": "2.391, 1.009 joule", "PV3": "2.445, 1.071 joule"}}
    return json.dumps(result)

def readResultVoltages(exp_voltages_file):
    
    print("this process for read data from "+exp_voltages_file+" file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    df = pd.read_csv(
        path+exp_voltages_file,
        nrows=4, delimiter = ",",
        low_memory = True
    )

    #df['Bus'] = df['Bus'].astype(str)
    #df['pu1'] = df['pu1'].astype(float)
    #df['pu2'] = df['pu2'].astype(float)
    #df['pu3'] = df['pu3'].astype(float)

    print('Method 2: Starting Experiment')
    # timer starts
    start = time.time()
    # display information
    print('Show Infos:')
    df.info()
    print('')
    print('Show Top Three Rows')
    print(df.head(3))


    lv_lv1_pu=df.iloc[1,5]
    lv_lv2_pu=df.iloc[1,9]
    lv_lv3_pu=df.iloc[1,13]

    pcc_v1_pu=df.iloc[2,5]
    pcc_v2_pu=df.iloc[2,9]
    pcc_v3_pu=df.iloc[2,13]

    print(f'LV: V1(pu) : {lv_lv1_pu}')
    print(f'LV: V2(pu) : {lv_lv2_pu}')
    print(f'LV: V3(pu) : {lv_lv3_pu}')

    print(f'PCC: V1(pu) : {pcc_v1_pu}')
    print(f'PCC: V2(pu) : {pcc_v2_pu}')
    print(f'PCC: V3(pu) : {pcc_v3_pu}')

    lv = {'V1': lv_lv1_pu, 'V2': lv_lv2_pu, 'V3': lv_lv3_pu}
    pcc = {'V1': pcc_v1_pu, 'V2': pcc_v2_pu, 'V3': pcc_v3_pu}

    # timer ends
    end = time.time()
    print('\nExperiment Completed\nTotal Time: {:.2f} seconds'.format(end-start))

    result = {'status': True,'output_lv':lv,'output_pcc':pcc}
    return json.dumps(result)

def readResultpByPhase(p_phases_file):
    print("this process for read data from "+p_phases_file+" file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    #df = pd.read_csv(
    #    path+p_phases_file,
    #    nrows=7, delimiter = ",",
    #    low_memory = True
    #)
    df = pd.read_csv(path+p_phases_file)
    #df['Bus'] = df['Bus'].astype(str)
    #df['pu1'] = df['pu1'].astype(float)
    #df['pu2'] = df['pu2'].astype(float)
    #df['pu3'] = df['pu3'].astype(float)

    print('Method 2: Starting Experiment')
    # timer starts
    start = time.time()
    # display information
    print('Show Infos:')
    df.info()
    #print(''+df.iloc[1,])
    print('Show Top Three Rows')
    #print(df.head(3))

    #kw1=df.iloc[0,3]
    #kw2=df.iloc[0,5]
    #kw3=df.iloc[0,7]

    #pv1_joule=df.iloc[0,4]
    #pv2_joule=df.iloc[0,6]
    #pv3_joule=df.iloc[0,8]


    with open(path+p_phases_file,"r") as f:
        r = csv.DictReader(f, delimiter =";")
        for i, line in enumerate(r):
                #print (i)
                if(i==0):
                    #print (line)
                    #print(line, "is of type", type(line))
                    for key, value in line.items():
                        #print(f'{key}={value}')
                        data_raw=value
                    print(data_raw)
                    colData = data_raw.split(',')
                    print(f'lenght :{len(colData)}')

                
  

    kw1=convertValue(float(colData[12]))
    kw2=convertValue(float(colData[14]))
    kw3=convertValue(float(colData[16]))

    pv1_joule=convertValue(float(colData[13]))
    pv2_joule=convertValue(float(colData[15]))
    pv3_joule=convertValue(float(colData[17]))

    print(f'Line PV1 : {kw1},{pv1_joule}')
    print(f'Line PV2 : {kw2},{pv2_joule}')
    print(f'Line PV3 : {kw3},{pv3_joule}')


    line = {'PV1': kw1, 'PV2': kw2, 'PV3': kw3}
    kilojoule  = {'PV1': pv1_joule, 'PV2': pv2_joule, 'PV3': pv3_joule}
    output_line = {'PV1': str(kw1)+", "+str(pv1_joule)+" joule", 'PV2': str(kw2)+", "+str(pv2_joule)+" joule", 'PV3': str(kw3)+", "+str(pv3_joule)+" joule"}
    #output_line={}
    # timer ends
    end = time.time()
    print('\nExperiment Completed\nTotal Time: {:.2f} seconds'.format(end-start))

    result = {'status': True,'line':line,'kilojoule':kilojoule,'output_line':output_line}
    return json.dumps(result)

def generateChart(data_lv,data_pcc,length,timestamp):
    print("this call generateChart.")
    dir_name = getattr(settings, "CHART_PATH", None)
    autoscale = getattr(settings, "AUTOSCALE", False)
    #dir_name = "D:/Work/Git/Python/powercal/static/images/"

    plt.rcParams["savefig.directory"] = os.chdir(os.path.dirname(dir_name))

    verts = [
            (0.0, data_lv["V1"]),   # P0
            (length, data_pcc["V1"]),  # P1
        ]
    verts2 = [
            (0.0, data_lv["V2"]),  # P2
            (length, data_pcc["V2"]),  # P3
        ]
    verts3 = [
            (0.0, data_lv["V3"]),  # 
            (length, data_pcc["V3"]),  # 
        ]

    codes = [
            mpath.Path.MOVETO,
            mpath.Path.LINETO,
        ]
    
    codes2 = [
            mpath.Path.MOVETO,
            mpath.Path.LINETO,
        ]
    
    codes3 = [
            mpath.Path.MOVETO,
            mpath.Path.LINETO,
        ]

    path = mpath.Path(verts, codes)
    path2 = mpath.Path(verts2, codes2)
    path3 = mpath.Path(verts3, codes3)

    fig, ax = plt.subplots()
    patch = patches.PathPatch(path, facecolor='none', lw=2)
    patch2 = patches.PathPatch(path2, facecolor='none', lw=2)
    patch3 = patches.PathPatch(path3, facecolor='none', lw=2)

    ax.add_patch(patch)
    ax.add_patch(patch2)
    ax.add_patch(patch3)

    ax.grid()

    xs, ys = zip(*verts)
    ax.plot(xs, ys, '', lw=2, color='red', ms=10)

    xs2, ys2 = zip(*verts2)
    ax.plot(xs2, ys2, '', lw=2, color='yellow', ms=10)

    xs3, ys3 = zip(*verts3)
    ax.plot(xs3, ys3, '', lw=2, color='blue', ms=10)

    #ax.set_aspect('auto')
    #ax.set_xlim(xmin=0.0, xmax=pos04)
    
    if(autoscale):
        ax.set_aspect('auto')
    else:
        ax.set_ybound(lower=0.9, upper=1.1)
        ax.set_xbound(lower=0.0, upper=length)


    #plt.style.use('seaborn-whitegrid')
    #xpoints = np.array([0, 6])
    #ypoints = np.array([0, 250])

    ax.set_title('L-N Voltage Profile\n',
    fontsize = 14, fontweight ='bold')

    #plt.plot(xpoints, ypoints)
    # plt.show()


    title = "chart_"+timestamp
    #plt.xlabel("n iteration")
    #plt.legend(loc='upper left')
    #plt.title(title)

    plt.xlabel("Distance(km)")
    #plt.ylabel("Gold")

    #buffer = BytesIO()
    plt.savefig( title+".png", dpi=150)  # should before plt.show method
    #plt.savefig(buffer, title+".png", dpi=150) 
    #buffer.seek(0)
    #image_png = buffer.getvalue()
    #buffer.close()
    #graphic = base64.b64encode(image_png)
    #graphic = graphic.decode('utf-8')

    plt.close()
    result = {'status':'success','filename': title+".png"}

    return json.dumps(result)

def convertValue(value):
    if value < 0:
        return abs(value) #??????????????????????????? ???????????? ?????????
    else:
        return -abs(value) #?????????????????????????????? ???????????? ??????
    
def readResultLosses(exp_losses_file):
    print("this process for read data from "+exp_losses_file+" file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    df = pd.read_csv(
        path+exp_losses_file,
        nrows=3, delimiter = ",",
        low_memory = True
    )

    #df['Bus'] = df['Bus'].astype(str)
    #df['pu1'] = df['pu1'].astype(float)
    #df['pu2'] = df['pu2'].astype(float)
    #df['pu3'] = df['pu3'].astype(float)

    print('Method 2: Starting Experiment')
    # timer starts
    start = time.time()
    # display information
    print('Show Infos:')
    df.info()
    print('')
    print('Show Top Three Rows')
    print(df.head(3))

    p_loss_data=df.iloc[1,1]
    q_loss_data=df.iloc[1,2]

    print(f'P: p_loss_value : {p_loss_data}')
    print(f'Q: q_loss_value : {q_loss_data}')

    p_loss=p_loss_data/1000
    q_loss=q_loss_data/1000

    p_l_digi=np.format_float_positional(p_loss, unique=False, precision=3)
    q_l_digi=np.format_float_positional(q_loss, unique=False, precision=3)

    print(f'P_Losses : {p_loss}')
    print(f'Q_Losses : {q_loss}')

    print(f'P_Losses format : {p_l_digi}')
    print(f'Q_Losses format : {q_l_digi}')

    PQ = {'P': p_loss_data, 'Q': q_loss_data}
    Losses = {'p_loss': p_l_digi, 'q_loss': q_l_digi}


    # timer ends
    end = time.time()
    print('\nExperiment Completed\nTotal Time: {:.2f} seconds'.format(end-start))

    result = {'status': True,'output_pq':PQ,'output_losses':Losses}
    return json.dumps(result)