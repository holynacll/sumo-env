Docs:
  - https://sumo.dlr.de/pydoc/

Cenário:
  - network grid, com carros, semáforos e Ponto A e Ponto B
    - distancia eucl, manh e harvesine
  - ocorrência de acidente (parada de carro/congestionamento no local/fechamento da via)
    - dispara ambulância até o local e vai até o hospital mais próximo
  - criação do algoritmo de liberação de sinal verde
  - comparação entre cenários/features/níveis/...
  - extensão da linha de pesquisa para n caminhos...

  TODO
  - article: Analysis and modelling of road traffic using SUMO tooptimize the arrival time of emergency vehicles
   - melhorar cenario do acidente
   - quando um VE se aproximar de um sinal, tornar ele verde (já está mantendo verde, precisa virar verde, se tiver vermelho ou amarelo)
     - article: Modelling green waves for emergency vehicles usingconnected traffic data
   - priorizacao do VE
   - veiculos comuns priorizar veiculos de emergencia (dar passagem)
   - limitar e parametrizar tempo de simulação
   - criar hospitais parametrizavel
   - parametrizar as váriaveis do cenário
   - configurar parada do veículo de emergência no local do acidente
   - customizar/alternar algoritmos de roteamento
   - ajustar retorno dos veiculos na mesma via
   - ajustar controle de sinais "gggyyyrrr"

0.1 - $SUMO_HOME = "C:\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo"
0.2 - export SUMO_HOME="/home/acll/miniconda3/envs/sumo-env/lib/python3.11/site-packages/sumo"

1 - netgenerate --grid --grid.number=4 --grid.length=150 --default.lanenumber 2 --default-junction-type traffic_light --output-file=road.net.xml

2 - python $SUMO_HOME/tools/randomTrips.py -n road.net.xml -r route.rou.xml --seed 42 --validate --fringe-factor 1000

3 - add below code on first line into <routes> of the file route.rou.xml
  "<vType id="emergency_emergency" vClass="emergency" color="red"/>"

4 - python main.py

bibliografia:
Analysis and Modelling of Road Traffic Using SUMO to Optimize the Arrival Time of Emergency Vehicles - https://www.tib-op.org/ojs/index.php/scp/article/view/225/428 - https://www.youtube.com/watch?v=GlPf7TmuI9E (verificar o algoritmo)
Intelligent traffic management for emergency vehicles with a simulation case study - https://www.youtube.com/watch?v=7rpXvYsNFIE
A Programmer's Note on TraCI_tls, TraCI, and SUMO - https://intelaligent.github.io/tctb/post-learning-traci-tls.html
Quantifying the impact of connected and autonomous vehicles on traffic efficiency and safety in mixed traffic
https://core.ac.uk/download/pdf/147323687.pdf
https://easychair.org/publications/open/6KGt
https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=9264154
https://www.researchgate.net/publication/328406378_Urban_Traffic_Optimization_with_Real_Time_Intelligence_Intersection_Traffic_Light_System
https://people.engr.tamu.edu/guni/Papers/NeurIPS-signals.pdf
https://arxiv.org/pdf/2107.10146.pdf
Simulation of accident with V2X communication using SUMO-TraCI-Veins - https://www.youtube.com/watch?v=7TXngtcCPz4

refs:
Lane-Changing Model in SUMO
https://arxiv.org/pdf/2304.05982.pdf
https://cst.fee.unicamp.br/sites/default/files/sumo/sumo-roadmap.pdf
https://github.com/eclipse-sumo/sumo/issues/4312
https://www.researchgate.net/publication/37454736_TraCI_An_Interface_for_Coupling_Road_Traffic_and_Network_Simulators?enrichId=rgreq-481d19cd502f6889985e24af3c6715e4-XXX&enrichSource=Y292ZXJQYWdlOzM3NDU0NzM2O0FTOjk5NzQ2NDUwNTA5ODMyQDE0MDA3OTI4MTY1NTY%3D&el=1_x_3&_esc=publicationCoverPdf



bugs:
cars not stopping on red light: https://sourceforge.net/p/sumo/mailman/message/30703209/




 1935  python $SUMO_HOME/tools/randomTrips.py -n road.net.xml
 1936  python $SUMO_HOME/tools/assign/duaIterate.py -n road.net.xml -t trips.trips.xml -l 10
 1941  python $SUMO_HOME/tools/assign/one-shot.py -f 200 -n road.net.xml -t trips.trips.xml
 1942  python $SUMO_HOME/tools/randomTrips.py -n road.net.xml --seed 42 --validate
 1943  python $SUMO_HOME/tools/assign/one-shot.py -f 200 -n road.net.xml -t trips.trips.xml
 1948  python $SUMO_HOME/tools/randomTrips.py -n road.net.xml --seed 42 --validate
 1949  python $SUMO_HOME/tools/assign/one-shot.py -f 200 -n road.net.xml -t trips.trips.xml
 1957  netgenerate --grid --grid.number=2 --grid.length=150 --default.lanenumber 2 --default-junction-type traffic_light --output-file=road.net.xml
 1959  netgenerate --grid --grid.number=3 --grid.length=150 --default.lanenumber 2 --default-junction-type traffic_light --output-file=road.net.xml
 1968  netedit road.net.xml 
 1970  python $SUMO_HOME/tools/randomTrips.py -n road.net.xml --seed 42 --validate --fringe-factor 1000
 1971  netgenerate --grid --grid.number=3 --grid.length=150 --default.lanenumber 2 --default-junction-type traffic_light --output-file=road.net.xml
 1972  python $SUMO_HOME/tools/assign/one-shot.py -f 10 -n road.net.xml -t trips.trips.xml



