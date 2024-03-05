import os
import sys
import time
import optparse
os.environ['SUMO_HOME'] = "C:\\Users\\Alexandre Cury\\miniconda3\\envs\\sumo-env\\Lib\\site-packages\\sumo"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

# sumoBinary = os.path.join(tools, "sumo-gui")
# sumo_gui = 'sumo-gui'
# file = "cenary.sumocfg"
# sumoCmd = [sumo_gui, "-c", file]

import traci
from sumolib import checkBinary  # noqa
# traci.start(sumoCmd)

def check_tls(tls_id):
    print("checking tls_id: ", tls_id)
    print("ryg", traci.trafficlight.getRedYellowGreenState(tls_id))
    print("rygdef", traci.trafficlight.getAllProgramLogics(tls_id))
    print("lanes", traci.trafficlight.getControlledLanes(tls_id))
    print("links", traci.trafficlight.getControlledLinks(tls_id))
    print("program", traci.trafficlight.getProgram(tls_id))
    print("phase", traci.trafficlight.getPhase(tls_id))
    print("phaseName", traci.trafficlight.getPhaseName(tls_id))
    print("switch", traci.trafficlight.getNextSwitch(tls_id))


def shouldContinueSim():
    """Checks that the simulation should continue running.
    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False

def run():
    step = 0
    while shouldContinueSim():
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()
        for vehicle_id in vehicles:
            type_id = traci.vehicle.getTypeID(vehicle_id)
            if type_id == 'emergency_emergency':
                print(type_id)
                """
                Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
                cada tls está em ordem crescente de distância 
                The lanePosition is the driving distance from the start of the edge (road) in meters
                """
                next_tls_set = traci.vehicle.getNextTLS(vehicle_id)
                print("next tls for vehicle emergency:", vehicle_id, " is ", next_tls_set)
                for tls in next_tls_set:
                    # get tls
                    tls_id = tls[0]
                    tls_index = tls[1]
                    vehicle_distance_to_tls = tls[2]
                    tls_state = tls[3]
                    if vehicle_distance_to_tls < 40:
                        if tls_state in ('g', 'G'):
                            # traci.trafficlight.setPhase(tls_id, 0)
                            traci.trafficlight.setPhaseDuration(tls_id, 5)
                    # check_tls(tls_id)
                    # tls_phases = traci.trafficlight.getRedYellowGreenState(tls_id)
                    # print(tls_phases)
                    # for index, phase in enumerate(tls_phases):
                    #     if phase in ('g', 'G'):
                    #         # traci.trafficlight.setPhase(tls_id, int(index))
                    #         traci.trafficlight.setPhaseDuration(tls_id, 10)
                    #         break
                    
                    # vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
                    # time_to_tls = tls_distance/vehicle_speed
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
        
        # if step%10==0:
        #     for i in range(0, len(vehicles)):
        #         print(vehicles[i])
        #         traci.vehicle.setSpeed(vehicles[i], 15)  
        #         traci.gui.toggleSelection(vehicles[i])
                
                
        #     print("Speed ", vehicles[i], ": ", traci.vehicle.getSpeed(vehicles[i]), " m/s")
        #     print("CO2Emission ", vehicles[i], ": ", traci.vehicle.getCO2Emission(vehicles[i]), " mg/s")
        #     print("EdgeID of veh ", vehicles[i], ": ", traci.vehicle.getRoadID(vehicles[i]))
        #     print("Distance ", vehicles[i], ": ", traci.vehicle.getDistance(vehicles[i]), " m")
        step += 1

    #get network parameters
    IDsOfEdges=traci.edge.getIDList()
    print("IDs of the edges:", IDsOfEdges)
    IDsOfJunctions=traci.junction.getIDList()
    print("IDs of junctions:", IDsOfJunctions)

    traci.close()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "cenary.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
