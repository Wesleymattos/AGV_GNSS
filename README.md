# AGV_GNSS
Data da ultima atualização: 07/11/2025
Autor: Wesley de Mattos
versão: 2.0.0

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

Data: 06/11/2025
horário: 15:20
versão: 1.0.4
Melhoria: Foi o parsing de GPGSA com PDOP, HDOP e VDOP

Data: 06/11/2025
horário: 20:26
versão: 1.0.5
Melhoria: Foi adicionado o parsing de GPGST, RMS (erro total), Sigma Latitude, Sigma Longitude, Erro Semi-eixo, Maior, Erro Semi-eixo Menor, Orientação da Elipse

Data: 06/11/2025
horário: 21:18
versão: 1.0.6
Melhoria: Foi adicionado centralizado os nomes de receptores 

Data: 07/11/2025
horário: 09:01
versão: 1.0.7
Melhoria: Foi adicionado informações ao passar o mouse por cima das variáveis

Data: 07/11/2025
horário: 15:36
versão: 1.0.8
Melhoria: Foi adicionado o novo HTML de média de valores

Data: 07/11/2025
horário: 16:25
versão: 1.0.9
Melhoria: Foi adicionado uma correção na pontuação da média de valores, satélites e longitude e latitude

Data: 07/11/2025
horário: 16:48
versão: 1.0.10
Melhoria: Foi adicionado uma nova função gráficos no comparador de nmea média de valores




######################################################################### Vamos seguir o padrão de versionamento de código, o versionamento semântico, Major, minor.patch

Correção (patch) - 1.0.0 / 1.0.1 = corrigiu bug
Nova função compatível - 1.0.0 / 1.1.0 = Adicionou recurso
Mudança grande - 1.2.5 / 2.0.0 = Reescreveu ou alterou compatibilidade 


--------------------------------------------------------------------------------------


Data: 08/11/2025
horário: 11:43
versão: 1.1.10
Melhoria: Foi adicionado uma nova função gráficos em tempo real

Data: 08/11/2025
horário: 12:21
versão: 1.1.11
Melhoria: Foi adicionado uma correção para sicronismo de dados entre o gráfico de satélites no mesmo tempo

Data: 08/11/2025
horário: 13:03
versão: 1.1.12
Melhoria: corrigi o problema do zoom do mapa 2

Data: 09/11/2025
horário: 19:22
versão: 1.2.12
Melhoria: Adicionado gráfico vdop ao lado de satelite

Data: 09/11/2025
horário: 22:48
versão: 1.3.12
Melhoria: Adicionado um chat no aplicativo

Data: 10/11/2025
horário: 09:55
versão: 1.3.13
Melhoria: receiver 2 atualizado para cor azul

Data: 10/11/2025
horário: 10:00
versão: 1.3.14
Melhoria: precisão do gráfico de HDOP foi aumentado

Data: 14/11/2025
horário: 17:30
versão: 2.0.0
Melhoria: Foi adicionado o terceiro receptor, melhorias no mapa comparador, Drive Simulator AGV, e o aplicativo python atualizado para log_remote_usbv2.6

