

from boleta.desempaquetadores import Desempaquetador
from estado.estados_impresion import ImpresionStatus
from impresion.handlers import ConectionHandler


impresionStatus = ImpresionStatus()
conectionHandler = ConectionHandler(impresionStatus)
desempaquedator = Desempaquetador(impresionStatus)

impresionStatus._observadores_base = impresionStatus._observadores

# Ejecutar el bucle
ciclo = True
cont = 0
while ciclo:
    print("")
    print("conectando...")
    impresionStatus.conectar()
    print("")
    print("desempaquetando...")
    impresionStatus.desempaquetar()  # Desempaquetar las boletas y establecer la cantidad de instancias
    print("")
    print("instanciando...")
    impresionStatus.instanciar()
    print("")
    print("imprimiendo...")
    impresionStatus.imprimir()
    print("")
    print("conectando para marcar...")
    impresionStatus.marcar()

    print("")
    print("marcado...")
    print(impresionStatus.get_status())
    cont += 1
    if cont > 2:
        ciclo = False
    else:
        ciclo = True