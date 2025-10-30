# AGV_GNSS

Sistemas remoto para coleta de dados em tempo real de receptores GNSS utilizando um AGV!

Neste projeto nós temos: 
1. Aplicativo web Log Remote AGV.
2. Software em python para interação do Log Remote AGV e os relés do AGV.
3. Software em python para o Sistema de leitura do receptores do AGV via USB e envio para o Firebase.
4. Firmare em c para o Esp32 do sistema de relé do AGV.
5. Firmware em c para o Esp32 do sistema opcional onde o Esp32 faz a leitura dos receptores (descontinuado, pois foi decidido fazer esse sistema diretamente no Raspberry).
6. Software APK do aplicativo desenvolvido para Android baseado em web, permitindo a possibilidade de acessar pelo celular
