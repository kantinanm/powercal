from datetime import datetime
import json
import pandas as pd
from django.conf import settings
import time
import numpy as numpy
import csv as csv


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

  

    print(data)
    result = {'status': True,'filename':fileName,'timestamp':date_time}
    return json.dumps(result)

async def readResult(exp_voltages_file):
    print("this process for read csv file.")
    path = getattr(settings, "CSV_PATH", None) #get path

    #'D:/Work/OpenDSS/'+exp_voltages_file,
    #path+exp_voltages_file, 
    df = pd.read_csv(
        'D:/Work/OpenDSS/exp_voltages.csv',
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
    print(df.head(-3))


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