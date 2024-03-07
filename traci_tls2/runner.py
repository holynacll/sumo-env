import os
import sys
import time
import random
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
import traci.constants as tc
from sumolib import checkBinary  # noqa
# traci.start(sumoCmd)


def generate_routefile():
    random.seed(42)  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10
    pEW = 1. / 11
    pNS = 1. / 30
    with open("data/cross.rou.xml", "w") as routes:
        print("""<routes>
        <vType id="typeWE" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" \
guiShape="passenger"/>
        <vType id="typeNS" accel="0.8" decel="4.5" sigma="0.5" length="7" minGap="3" maxSpeed="25" guiShape="bus"/>

        <route id="right" edges="51o 1i 2o 52i" />
        <route id="left" edges="52o 2i 1o 51i" />
        <route id="down" edges="54o 4i 3o 53i" />""", file=routes)
        vehNr = 0
        for i in range(N):
            if random.uniform(0, 1) < pWE:
                print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pEW:
                print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
                    vehNr, i), file=routes)
                vehNr += 1
            if random.uniform(0, 1) < pNS:
                print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
                    vehNr, i), file=routes)
                vehNr += 1
        print("</routes>", file=routes)


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


def check_vehicle(vehicle_id):
    # Read current values
    print("Speed ", vehicle_id, ": ", traci.vehicle.getSpeed(vehicle_id), " m/s")
    print("CO2Emission ", vehicle_id, ": ", traci.vehicle.getCO2Emission(vehicle_id), " mg/s")
    print("EdgeID of veh ", vehicle_id, ": ", traci.vehicle.getRoadID(vehicle_id))
    print("Distance ", vehicle_id, ": ", traci.vehicle.getDistance(vehicle_id), " m")


def shouldContinueSim():
    """Checks that the simulation should continue running.
    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False

def run():
    step = 0
    junctionID = traci.junction.getIDList()[0]
    traci.junction.subscribeContext(
        junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1000000,
        [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED]
    )
    stepLength = traci.simulation.getDeltaT()
    accidents_num = 1
    allowed_vehicles_type_on_emergency = ['emergency']
    edges_start = ['51o', '52o','54o']
    while shouldContinueSim():
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()     
        if traci.simulation.getTime() > 250 and accidents_num > 0:
            some_vehicle_id = vehicles[0]
            road_id = traci.vehicle.getRoadID(some_vehicle_id)
            if road_id in edges_start:
                print(f"road_id: {road_id} pass")
                pass

            # check vehicle
            check_vehicle(some_vehicle_id)
            
            # create accident
            traci.vehicle.setSpeedMode(some_vehicle_id, 0)
            traci.vehicle.setSpeed(some_vehicle_id, 0)
            traci.vehicle.highlight(some_vehicle_id, (0, 0, 255, 255))
            # broadcast message to vanets? how do i announce an accident?
            #close the lane/edge
            road_id = traci.vehicle.getRoadID(some_vehicle_id)
            traci.edge.setAllowed(road_id, allowed_vehicles_type_on_emergency)
            # get_position_vehicle
            # x, y = traci.vehicle.getPosition(some_vehicle_id)
            # traci.poi.add("140907752#1", x, y, color=(255, 0, 0), type="shop")
            traci.route.add(f"trip_{step}", ["54o", road_id])
            traci.vehicle.add(f"newEmergencyVeh-{step}", f"trip_{step}")
            traci.vehicle.highlight(f"newEmergencyVeh-{step}", (0, 255, 255, 255))
            traci.vehicle.setVehicleClass(f"newEmergencyVeh-{step}", "emergency")
            traci.vehicle.setSpeed(f"newEmergencyVeh-{step}", 15.0)
            traci.vehicle.setSpeedMode(f"newEmergencyVeh-{step}", 0)

                    # <vType id="typeVE" vClass="emergency" color="red"/>

            #sen
            accidents_num -= 1
        for vehicle_id in vehicles:
            type_id = traci.vehicle.getTypeID(vehicle_id)
            if type_id == 'emergency_emergency':
                """
                Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
                cada tls está em ordem crescente de distância 
                The lanePosition is the driving distance from the start of the edge (road) in meters
                """
                next_tls_set = traci.vehicle.getNextTLS(vehicle_id)
                # print("next tls for vehicle emergency:", vehicle_id, " is ", next_tls_set)
                for tls in next_tls_set:
                    # get tls
                    tls_id = tls[0]
                    tls_index = tls[1]
                    vehicle_distance_to_tls = tls[2]
                    tls_state = tls[3]
                    if vehicle_distance_to_tls < 40:
                        if tls_state in ('g', 'G'):
                            traci.trafficlight.setPhaseDuration(tls_id, 5)
                            # traci.trafficlight.setPhase(tls_id, 0)
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
        scResults = traci.junction.getContextSubscriptionResults(junctionID)
        halting = 0
        if scResults:
            relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
            # compute values corresponding to summary-output
            running = len(relSpeeds)
            halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
            meanSpeedRelative = sum(relSpeeds) / running
            timeLoss = (1 - meanSpeedRelative) * running * stepLength
        print(traci.simulation.getTime(), timeLoss, halting)
        step += 1

    #get network parameters
    # IDsOfEdges=traci.edge.getIDList()
    # print("IDs of the edges:", IDsOfEdges)
    # IDsOfJunctions=traci.junction.getIDList()
    # print("IDs of junctions:", IDsOfJunctions)

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
    generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
