import os
import sys
import time
os.environ['SUMO_HOME'] = "C:\\Users\\Alexandre Cury\\miniconda3\\envs\\sumo-env\\Lib\\site-packages\\sumo"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

def shouldContinueSim():
    """Checks that the simulation should continue running.
    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False

sumoBinary = os.path.join(tools, "sumo-gui")
sumo_gui = 'sumo-gui'
file = "my_sumo_net.sumocfg"
sumoCmd = [sumo_gui, "-c", file]

import traci
traci.start(sumoCmd)

step = 1
while shouldContinueSim():
    print(step)
    time.sleep(0.5)
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()
    
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
