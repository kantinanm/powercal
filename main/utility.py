from datetime import datetime
import json


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
    result = {'status': True,'filename':fileName}
    return json.dumps(result)