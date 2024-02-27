Cenário: 
  - network grid, com carros, semáforos e *hospitais*.
  - ocorrência de acidente (parada de carro/congestionamento no local/fechamento da via)
    - dispara ambulância até o local e vai até o hospital mais próximo
  - criação do algoritmo de liberação de sinal verde
  - comparação entre cenários/features/níveis/...
  - extensão da linha de pesquisa para n caminhos...
    

0 - $SUMO_HOME = "C:\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo"

1 - netgenerate --grid --grid.number=4 --grid.length=75 -j traffic_light --output-file=cenary.net.xml

2 - python $SUMO_HOME/tools/randomTrips.py -n cenary.net.xml -o odtrips.car.xml -r cenary.car.rou.xml --prefix car --period 1 -p 2 --trip-attributes='color=\"0,0,1\"'

3 - python $SUMO_HOME/tools/randomTrips.py -n cenary.net.xml -o odtrips.emergency.xml -r cenary.emergency.rou.xml --prefix emergency --period 100 -p 10 --vehicle-class emergency --trip-attributes='color=\"1,0,0\"'

4 - python $SUMO_HOME/tools/generateParkingAreas.py -n cenary.net.xml -o parkingareas.add.xml --space-length 10 --probability 0.1

last - sumo-gui cenary.sumocfg


bibliografia:
Analysis and Modelling of Road Traffic Using SUMO to Optimize the Arrival Time of Emergency Vehicles - https://www.youtube.com/watch?v=GlPf7TmuI9E
Intelligent traffic management for emergency vehicles with a simulation case study - https://www.youtube.com/watch?v=7rpXvYsNFIE
A Programmer's Note on TraCI_tls, TraCI, and SUMO - https://intelaligent.github.io/tctb/post-learning-traci-tls.html

https://github.com/eclipse-sumo/sumo/issues/4312