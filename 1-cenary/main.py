import os
import sys
import time
os.environ['SUMO_HOME'] = "C:\\Users\\Alexandre Cury\\miniconda3\\envs\\sumo-env\\Lib\\site-packages\\sumo"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = os.path.join(tools, "sumo-gui")
sumo_gui = 'sumo-gui'
file = "cenary.sumocfg"
sumoCmd = [sumo_gui, "-c", file]

import traci
traci.start(sumoCmd)

def shouldContinueSim():
    """Checks that the simulation should continue running.
    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False

step = 1
while shouldContinueSim():
    print(step)
    time.sleep(0.5)
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()
    for vehicle_id in vehicles:
        type_id = traci.vehicle.getTypeID(vehicle_id)
        classname = traci.vehicle.getVehicleClass(type_id)
        if classname == 'emergency':
            print(classname)
            next_tls = traci.vehicle.getNextTLS(vehicle_id)
            print("next tls for vehicle emergency:", vehicle_id, " is ", next_tls)
    # tls_id_list = traci.trafficlight.getIDList()
    # for tls_id in tls_id_list:
    #     links_controlleds = traci.trafficlight.getControlledLinks(tls_id)
    #     print('links controllers: ', links_controlleds)
    #     for links_set_list in links_controlleds:
    #         for link_set in links_set_list:
    #             for link in link_set:
    #                 print('link: ', link)
    #                 vehiclesblock = traci.trafficlight.getBlockingVehicles(tls_id, str(link))
    #                 print('cars blocked', vehiclesblock)
    # print(edges)
    # for edge_id in edges:
    #     if traci.inductionloop.getLastStepVehicleNumber(edge_id) > 0:
    #         print(f"carro passou pela edge {edge_id}")
    
    if step%10==0:
        for i in range(0, len(vehicles)):
           print(vehicles[i])
           traci.vehicle.setSpeedMode(vehicles[i], 0)
           traci.vehicle.setSpeed(vehicles[i], 15)  
           traci.gui.toggleSelection(vehicles[i])
           
           
           print("Speed ", vehicles[i], ": ", traci.vehicle.getSpeed(vehicles[i]), " m/s")
           print("CO2Emission ", vehicles[i], ": ", traci.vehicle.getCO2Emission(vehicles[i]), " mg/s")
           print("EdgeID of veh ", vehicles[i], ": ", traci.vehicle.getRoadID(vehicles[i]))
           print("Distance ", vehicles[i], ": ", traci.vehicle.getDistance(vehicles[i]), " m")
    step += 1

#get network parameters
IDsOfEdges=traci.edge.getIDList()
print("IDs of the edges:", IDsOfEdges)
IDsOfJunctions=traci.junction.getIDList()
print("IDs of junctions:", IDsOfJunctions)

traci.close()
