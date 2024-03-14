import os
import sys
import time
import optparse
os.environ['SUMO_HOME'] = "/home/acll/miniconda3/envs/sumo-env/lib/python3.11/site-packages/sumo"

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


def improve_traffic_on_accident(emergency_route_id):
    vehicles = traci.vehicle.getIDList()
    for veh_id in vehicles:
        next_roads_list = traci.vehicle.getRoute(veh_id)
        # print('next_roads_lists:', next_roads_list, 'emergency_route_id:', emergency_route_id)
        if emergency_route_id in next_roads_list:
            # check_vehicle(veh_id)
            # traci.edge.adaptTraveltime(road_id,traci.edge.getTraveltime(road_id))
            traci.vehicle.setAdaptedTraveltime(veh_id, emergency_route_id, float('inf'))
            traci.vehicle.rerouteTraveltime(veh_id)


def monitor_emergency_vehicles(monitor_emergency_vehicles_list):
    for monitor_emergency_vehicle in monitor_emergency_vehicles_list:
        veh_accidented_id = monitor_emergency_vehicle['veh_accidented_id']
        veh_emergency_id = monitor_emergency_vehicle['veh_emergency_id']
        emergency_route_id = monitor_emergency_vehicle['emergency_route_id']
        arrival_pos = monitor_emergency_vehicle['arrival_pos']
        hospital_pos = monitor_emergency_vehicle['hospital_pos']
        print('monitoring', monitor_emergency_vehicles_list)
        improve_traffic_on_accident(emergency_route_id)
        actual_road = traci.vehicle.getRoadID(veh_emergency_id)
        print('actual_road:', actual_road, 'emergency_route_id:', emergency_route_id)
        if actual_road == emergency_route_id:
            actual_pos = traci.vehicle.getDrivingDistance(veh_emergency_id, actual_road, arrival_pos)
            print(actual_pos, arrival_pos)
            if  actual_pos >= arrival_pos - 0.01:
                # new_emergency_route_id_back_to_hospital = f"rou_emergency_{traci.simulation.getTime()}"
                # traci.route.add(routeID=new_emergency_route_id_back_to_hospital, edges=[actual_road, hospital_pos])
                # traci.vehicle.changeTarget(veh_emergency_id, hospital_pos)
                traci.vehicle.remove(veh_accidented_id)
                traci.edge.setMaxSpeed(emergency_route_id, 50)
                # stop vehicle for some duration
                # rerouter emergency vehicle to hospital
                # release vehicle accidented


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
    road_id_accidented_list = []
    monitor_emergency_vehicles_list = []
    hospital_pos = 'A1B1'
    while shouldContinueSim():
        traci.simulationStep()
        monitor_emergency_vehicles(monitor_emergency_vehicles_list)
        vehicles = traci.vehicle.getIDList()
        # em um dado momento, acidente ocorre
        if traci.simulation.getTime() > 50 and accidents_num > 0:
            veh_accidented_id = vehicles[0]
            road_id_accidented = traci.vehicle.getRoadID(veh_accidented_id)
            # if (road_id == 'C1B1'):
            accidents_num -= 1
            # check_vehicle(veh_accidented_id)
            # create accident
            # Regard safe speed
            traci.edge.setMaxSpeed(road_id_accidented, 0.1)
            traci.vehicle.setSpeedMode(veh_accidented_id, 0)
            traci.vehicle.setSpeed(veh_accidented_id, 0)
            traci.vehicle.highlight(veh_accidented_id, (0, 0, 255, 255))
            
            emergency_route_id = f"rou_emergency_{traci.simulation.getTime()}"
            veh_emergency_id = f"veh_emergency_{traci.simulation.getTime()}"
            arrival_pos = traci.vehicle.getLanePosition(veh_accidented_id)
            traci.route.add(routeID=emergency_route_id, edges=[hospital_pos, road_id_accidented])
            traci.vehicle.add(
                vehID=veh_emergency_id,
                routeID=emergency_route_id,
                typeID="emergency_emergency",
                depart='now',
                departLane='best',
                departPos='base',
                departSpeed='0',
                arrivalLane='current',
                arrivalPos=arrival_pos,
                arrivalSpeed='current'
            )
            monitor_emergency_vehicles_list.append({
                'veh_accidented_id': veh_accidented_id,
                'veh_emergency_id':veh_emergency_id,
                'emergency_route_id': road_id_accidented,
                'arrival_pos': arrival_pos,
                'hospital_pos': hospital_pos,
            })
            # broadcast message to vanets? how do i announce an accident?
            # traci.edge.setAllowed(road_id, allowed_vehicles_type_on_emergency)
            # x, y = traci.vehicle.getPosition(some_vehicle_id)
            # traci.poi.add("140907752#1", x, y, color=(255, 0, 0), type="shop")

        # if traci.simulation.getTime()%500==0 and accidents_num == 0:
        #     accidents_num -= 1
        #     traci.vehicle.setSpeedMode(some_vehicle_id, 1)
        #     traci.vehicle.setSpeed(some_vehicle_id, 40.0)
        #     traci.edge.setMaxSpeed(road_id, 50.0)
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
        # scResults = traci.junction.getContextSubscriptionResults(junctionID)
        # halting = 0
        # if scResults:
        #     relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
        #     # compute values corresponding to summary-output
        #     running = len(relSpeeds)
        #     halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
        #     meanSpeedRelative = sum(relSpeeds) / running
        #     timeLoss = (1 - meanSpeedRelative) * running * stepLength
        # print(traci.simulation.getTime(), timeLoss, halting)
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
    # generate_routefile()

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "one_shot_10.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
