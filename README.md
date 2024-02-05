links:
https://www.openstreetmap.org/export#map=15/-15.8011/-47.8885
https://sumo.dlr.de/docs/Networks/Import/OpenStreetMap.html
https://arxiv.org/pdf/2304.05982.pdf
https://towardsdatascience.com/how-to-simulate-traffic-on-urban-networks-using-sumo-a2ef172e564
https://towardsdatascience.com/visualizing-real-time-traffic-patterns-using-here-traffic-api-5f61528d563
https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html
Script:
0 -
export $SUMO_HOME = "C:\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo"

1 - 
netconvert --osm map.osm --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated -o my_sumo_net.net.xml

2 - 
polyconvert --net-file my_sumo_net.net.xml --osm-files map.osm --type-file osmPolyconvert.typ.xml -o my_sumo_net.poly.xml

3 - 
python $SUMO_HOME/tools/edgesInDistricts.py -n my_sumo_net.net.xml -t my_sumo_net.poly.xml -o TAZ.xml

4 -
python $SUMO_HOME/tools/randomTrips.py -n my_sumo_net.net.xml -o odtrips.xml --begin 0 --end 1 --period 1 --flows 50
<!-- od2trips -v --taz-files TAZs.taz.xml --vtype passenger --prefix car
--od-matrix-files OD_matrix.od -o output/output.odtrips.xml -->

5 -
duarouter --net-file my_sumo_net.net.xml --route-files od2trips.out.xml --output-file duarouter.rou.xml

6 -
python $SUMO_HOME/tools/route/route2OD.py -r duarouter.rou.xml -a TAZ.xml -o OD_matrix.xml

7 -
make the simulate.sumocfg file
<configuration>
    <input>
        <net-file value="test.net.xml"/>
        <route-files value="test.rou.xml"/>
        <additional-files value="test.add.xml"/>
    </input>
</configuration>



Explain:

1 - Importanting the network
Extract a map osm from OpenStreetMap and convert to a road network. Or generate a random road network utilizing netgenerate;

Generate road network randomly:
netgenerate --grid --grid.number=10 --grid.length=400
--output-file=MySUMOFile.net.xml

convert OSM extracted from OpenStreeMap:
netconvert --osm my_osm_net.xml -o my_sumo_net.net.xml
 --geometry.remove --ramps.guess --junctions.join --tls.guess-signals --tls.discard-simple --tls.join --tls.default-type actuated

--geometry.remove : Simplifies the network (saving space) without changing topology
--ramps.guess : Acceleration/Deceleration lanes are often not included in OSM data. This option identifies roads that likely have these additional lanes and adds them
--junctions.join : See #Junctions
--tls.guess-signals --tls.discard-simple --tls.join : See #Traffic_Lights
--tls.default-type actuated : Default static traffic lights are defined without knowledge about traffic patterns and may work poorly in high traffic

2 -  Import the Traffic Analysis Zones (TAZs)
import traffic analysis zones definitions. TAZs are polygons that delimitates an urban area

polyconvert --shapefile-prefix UrbAdm_Monitoring_District

3 - Trips Generation
For each vehicle, assign origin and destination into the road network. This can be done using real traffic data or randomly

4 - Traffic Assignment
Model the traffic flow (inteded as the set of routes assigned to vehicles). The traffic flow can be generated randomly or starting from OD matrices and using a routing algorithm based on classical methods as A*;

5 - Simulation
Simulate the traffic model using the defined network and traffic flow;

6 - Output Configuration
output information generated from the simulation that can be used for traffic analysis purposes;

python "..\..\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo\tools\randomTrips.py"


python "..\..\..\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo\tools\randomTrips.py" -n udemy.net.xml -o flows.xml --begin 0 --end 1 --period 1 --flows


jtrrouter --route-files=flows.xml --net-file=udemy.net.xml --output-file=grid.rou.xml --begin 0 --end 10000 --accept-all-destinations



python "..\..\..\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo\tools\generateContinuousRerouters.py" -n udemy.net.xml --end 10000 --begin -o rerouter.add.xml