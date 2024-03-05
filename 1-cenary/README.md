Cenário: 
  - network grid, com carros, semáforos e Ponto A e Ponto B
    - distancia eucl, manh e harvesine
  - ocorrência de acidente (parada de carro/congestionamento no local/fechamento da via)
    - dispara ambulância até o local e vai até o hospital mais próximo
  - criação do algoritmo de liberação de sinal verde
  - comparação entre cenários/features/níveis/...
  - extensão da linha de pesquisa para n caminhos...
    

0 - $SUMO_HOME = "C:\Users\Alexandre Cury\miniconda3\envs\sumo-env\Lib\site-packages\sumo"

1 - netgenerate --grid --grid.number=4 --grid.length=150 --default-junction-type traffic_light --output-file=cenary.net.xml 

2 - python $SUMO_HOME/tools/randomTrips.py -n cenary.net.xml -o odtrips.car.xml -r cenary.car.rou.xml --prefix car --period 1 -p 2 --trip-attributes='color=\"0,0,1\" accel=\"0.8\" decel=\"4.5\" sigma=\"0.5\" length=\"5\" minGap=\"2.5\" maxSpeed=\"16.67\" guiShape=\"passenger\"'

3 - python $SUMO_HOME/tools/randomTrips.py -n cenary.net.xml -o odtrips.emergency.xml -r cenary.emergency.rou.xml --prefix emergency --period 1000 -p 150 --vehicle-class emergency --trip-attributes='color=\"1,0,0\"'

4 - python $SUMO_HOME/tools/generateParkingAreas.py -n cenary.net.xml -o parkingareas.add.xml --space-length 10 --probability 0.1

last - sumo-gui cenary.sumocfg


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

refs:
Lane-Changing Model in SUMO
https://arxiv.org/pdf/2304.05982.pdf
https://cst.fee.unicamp.br/sites/default/files/sumo/sumo-roadmap.pdf
https://github.com/eclipse-sumo/sumo/issues/4312
https://www.researchgate.net/publication/37454736_TraCI_An_Interface_for_Coupling_Road_Traffic_and_Network_Simulators?enrichId=rgreq-481d19cd502f6889985e24af3c6715e4-XXX&enrichSource=Y292ZXJQYWdlOzM3NDU0NzM2O0FTOjk5NzQ2NDUwNTA5ODMyQDE0MDA3OTI4MTY1NTY%3D&el=1_x_3&_esc=publicationCoverPdf



bugs:
cars not stopping on red light: https://sourceforge.net/p/sumo/mailman/message/30703209/