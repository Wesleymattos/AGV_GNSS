# AGV_GNSS
Data da ultima atualização: 05/11/2025
autor: Wesley de Mattos
Versão: 1.0.3

observação: A apartir do dia 05/11/2025 o Log Remote Agv ganhou sua primeira versão oficial 1.0.0


Sistemas remoto para coleta de dados em tempo real de receptores GNSS utilizando um AGV!

Neste projeto nós temos: 
1. Aplicativo web Log Remote AGV.
2. Software em python para interação do Log Remote AGV e os relés do AGV.
3. Software em python para o Sistema de leitura do receptores do AGV via USB e envio para o Firebase.
4. Firmare em c para o Esp32 do sistema de relé do AGV.
5. Firmware em c para o Esp32 do sistema opcional onde o Esp32 faz a leitura dos receptores (descontinuado, pois foi decidido fazer esse sistema diretamente no Raspberry).
6. Software APK do aplicativo desenvolvido para Android baseado em web, permitindo a possibilidade de acessar pelo celular
7. Pasta com os projetos Android do aplicativo android 





#######################################################################
MELHORIAS POR VERSÕES

Data: 05/11/2025
horário: 21:41
versão: 1.0.1
Melhoria: Foi adicionado o mapa comparativo

Data: 06/11/2025
horário: 10:52
versão: 1.0.2
Melhoria: Foi adicionado medida no mapa comparativo

Data: 06/11/2025
horário: 14:45
versão: 1.0.3
Melhoria: Foi adicionado o HDOP do parsing GPGGA