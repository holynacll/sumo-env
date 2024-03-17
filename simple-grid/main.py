import os
import sys
import time
import optparse
import random
import traceback
os.environ['SUMO_HOME'] = "/home/acll/miniconda3/envs/sumo-env/lib/python3.11/site-packages/sumo"

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import traci.constants as tc
from sumolib import checkBinary  # noqa

monitor_emergency_vehicles_list = []
hospital_pos = 'A1B1'

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


def get_network_parameters():
    IDsOfEdges=traci.edge.getIDList()
    print("IDs of the edges:", IDsOfEdges)
    IDsOfJunctions=traci.junction.getIDList()
    print("IDs of junctions:", IDsOfJunctions)

def get_statistics_from_timeloss_and_halting(junction_id):
    scResults = traci.junction.getContextSubscriptionResults(junction_id)
    stepLength = traci.simulation.getDeltaT()
    halting = 0
    if scResults:
        relSpeeds = [d[tc.VAR_SPEED] / d[tc.VAR_ALLOWED_SPEED] for d in scResults.values()]
        # compute values corresponding to summary-output
        running = len(relSpeeds)
        halting = len([1 for d in scResults.values() if d[tc.VAR_SPEED] < 0.1])
        meanSpeedRelative = sum(relSpeeds) / running
        timeLoss = (1 - meanSpeedRelative) * running * stepLength
    print(traci.simulation.getTime(), timeLoss, halting)


def shouldContinueSim():
    """Checks that the simulation should continue running.
    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False


def improve_traffic_on_accidented_road(vehicles):
    for monitor_emergency_vehicle in monitor_emergency_vehicles_list:
        emergency_route_id = monitor_emergency_vehicle['emergency_route_id']
        for veh_id in vehicles:
            type_id = traci.vehicle.getTypeID(veh_id)
            if type_id != 'emergency_emergency':
                next_roads_list = traci.vehicle.getRoute(veh_id)
                if emergency_route_id in next_roads_list:
                    traci.edge.adaptTraveltime(emergency_route_id,traci.edge.getTraveltime(emergency_route_id))
                    traci.vehicle.rerouteTraveltime(veh_id)
                    if next_roads_list[-1] == emergency_route_id:
                        traci.vehicle.setColor(veh_id, color=(0, 100, 100))
                    else:
                        traci.vehicle.setColor(veh_id, color=(0, 255, 0))


def speed_road_recovery(emergency_route_id):
    MAX_SPEED_ROAD_RECOVERED = 50
    can_increase_max_speed = True
    for monitor_road in  monitor_emergency_vehicles_list:
        # se existe algum acidente em andamento
        if monitor_road['emergency_route_id'] == emergency_route_id:
            can_increase_max_speed = False
    if can_increase_max_speed:
        traci.edge.setMaxSpeed(emergency_route_id, MAX_SPEED_ROAD_RECOVERED)
        print("max speed road recovered")


def monitor_emergency_vehicles():
    MIN_ARRIVAL_DISTANCE_EMERGENCY_VEHICLE_AT_THE_ACCIDENT = 1.0
    for key, monitor_emergency_vehicle in enumerate(monitor_emergency_vehicles_list):
        veh_accidented_id = monitor_emergency_vehicle['veh_accidented_id']
        veh_emergency_id = monitor_emergency_vehicle['veh_emergency_id']
        emergency_route_id = monitor_emergency_vehicle['emergency_route_id']
        arrival_pos = monitor_emergency_vehicle['arrival_pos']
        hospital_pos = monitor_emergency_vehicle['hospital_pos']
        actual_road = traci.vehicle.getRoadID(veh_emergency_id)
        if actual_road == emergency_route_id:
            distance = traci.vehicle.getDrivingDistance(veh_emergency_id, actual_road, arrival_pos)
            if  distance < MIN_ARRIVAL_DISTANCE_EMERGENCY_VEHICLE_AT_THE_ACCIDENT:
                # stop emergency vehicle for some duration
                traci.vehicle.remove(veh_accidented_id)
                traci.vehicle.changeTarget(veh_emergency_id, hospital_pos)
                monitor_emergency_vehicles_list.pop(key)
                speed_road_recovery(emergency_route_id)
                


def create_accident_and_call_emergency_vehicle(vehicles):
    MAX_SPEED_ROAD_ACCIDENTED = 0.3
    random_number = random.randrange(0, len(vehicles))
    veh_accidented_id = vehicles[random_number]
    for monitor_emergency_vehicle in monitor_emergency_vehicles_list:
        if monitor_emergency_vehicle['veh_accidented_id'] == veh_accidented_id:
            print('verify how to handle with that case')
            return None
    road_id_accidented = traci.vehicle.getRoadID(veh_accidented_id)
    traci.edge.setMaxSpeed(road_id_accidented, MAX_SPEED_ROAD_ACCIDENTED)
    # traci.vehicle.setSpeedMode(veh_accidented_id, 0)
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
        arrivalPos='max',
        arrivalSpeed='current'
    )
    monitor_emergency_vehicles_list.append({
        'veh_accidented_id': veh_accidented_id,
        'veh_emergency_id':veh_emergency_id,
        'emergency_route_id': road_id_accidented,
        'arrival_pos': arrival_pos,
        'hospital_pos': hospital_pos,
    })


def improve_traffic_for_emergency_vehicle(vehicles):
    for veh_id in vehicles:
        type_id = traci.vehicle.getTypeID(veh_id)
        if type_id == 'emergency_emergency':
            """
            Return list of upcoming traffic lights [(tlsID, tlsIndex, distance, state), ...]
            cada tls está em ordem crescente de distância 
            The lanePosition is the driving distance from the start of the edge (road) in meters
            """
            next_tls_set = traci.vehicle.getNextTLS(veh_id)
            for tls in next_tls_set:
                tls_id = tls[0]
                vehicle_distance_to_tls = tls[2]
                tls_state = tls[3]
                if vehicle_distance_to_tls < 40:
                    if tls_state in ('g', 'G'):
                        traci.trafficlight.setPhaseDuration(tls_id, 5)


def run():
    step = 0
    junctionID = traci.junction.getIDList()[0]
    traci.junction.subscribeContext(
        junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 1000000,
        [tc.VAR_SPEED, tc.VAR_ALLOWED_SPEED]
    )

    try:
        while shouldContinueSim():
            traci.simulationStep()
            monitor_emergency_vehicles()
            vehicles = traci.vehicle.getIDList()
            if traci.simulation.getTime()%250 == 0:
                create_accident_and_call_emergency_vehicle(vehicles)
            improve_traffic_on_accidented_road(vehicles) # reroute vehicles to avoid of the aciddented road
            improve_traffic_for_emergency_vehicle(vehicles) # green wave
            # get_statistics_from_timeloss_and_halting(junctionID)    
            step += 1
        # get_network_parameters()
        traci.close()
    except Exception as e:
        print(traceback.format_exc())



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

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "config.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()
