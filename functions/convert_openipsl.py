#==========================================================================      
# Author: Marcelo de Castro Fernandes
#           
# Description: - - -
#==========================================================================
# ----- Init. libraries:
import time # importing time 
# ----- Opening the file:
start_time = time.time() # comecando a contar o tempo:
with open("IEEE_24_Barras_mod1.pwf", "r+") as input_file: # abre o arquivo para leitura
    for line in input_file:
        Content.append(line)                              # adiciona a linha a lista de linhas
input_file.close()                                        # fecha o arquivo: