import time
from core_dir.core import FiscalResponseHandler
from impresor.observers import Observador

    
class BoletaJson(Observador):
    ''' 
    Esta clase se encarga de manejar las boletas en formato JSON. 
    Observa el estado de impresión y mantiene un diccionario de tickets.
    '''
    def __init__(self, impresionStatus, boleta):
        ''' 
        Inicializa la boleta en formato JSON. 
        Toma un estado de impresión y una boleta como argumentos.
        '''
        super().__init__(impresionStatus)
        self.json = boleta
        self.id_boleta = self.json["id_boleta"]
        self.tipo = self.json["tipo"]
        self.comandos = self.json["comandos"]
        self.tickets = {}
        
            
    def instanciar_tickets(self):
        ''' 
        Instancia los tickets asociados a la boleta. 
        Recorre los comandos de la boleta y los instancia como objetos Ticket.
        Actualiza la cantidad de instancias de tickets.
        '''
        sublista = []
        n = 0
        self.tickets = {}
        if self.tipo == "Z":
            self.tickets[str(n)] = Ticket(self.impresionStatus, self.comandos)
            sublista = []
            n = n+1
            self.impresionStatus.incrementar_instancias_tickets(1)
        else:
            for comando in self.comandos:
                sublista.append(comando)
                
                if comando == "E":
                    self.tickets[str(n)] = Ticket(self.impresionStatus, sublista)
                    sublista = []
                    n = n+1
                    self.impresionStatus.incrementar_instancias_tickets(1)
        self.cantidad_instancias_tickets = n
        print("instanciando : ",self.cantidad_instancias_tickets) 
        
                 
    def enviar_impresiones(self):
        ''' 
        Envía las impresiones de los tickets. 
        Recorre los tickets y los imprime.
        '''
        for id, ticket in self.tickets.items():
            print(ticket)
            cant = 1 + int(id)
            print("{}/{}".format(cant,len(self.tickets.items())))
            ticket.imprimir()
            print("esto no,,, no???")
            self.impresionStatus.decrementar_impresiones(1)
            self.impresionStatus.decrementar_instancia_tickets(1)
            del ticket
        self.impresionStatus.decrementar_instancia(1, self)

    def actualizar(self):
        if self.habilitado():
            print("Habilitado: Instanciando tickets...")
            self.instanciar_tickets()

        if self.habilitado_impresion():
            print("Habilitado: Imprimiendo ticket...")
            self.enviar_impresiones()
        
    def habilitado(self):
        conectado =  not self.impresionStatus.conectando
        desempaquetando = not self.impresionStatus.desempaquetando
        instanciando = self.impresionStatus.instanciando
        imprimiendo = not self.impresionStatus.imprimiendo
        marcando = not self.impresionStatus.marcando
        boletas = self.impresionStatus.boletas == []
        instancias = self.impresionStatus.instancias > 0
        instancias_tickets = self.impresionStatus.instancias_tickets >= 0
        impresiones = self.impresionStatus.impresiones >= 0
        marcas = self.impresionStatus.marcas > 0
        
        return  conectado and desempaquetando and instanciando and imprimiendo and marcando and boletas and instancias and instancias_tickets and impresiones and marcas

    def habilitado_impresion(self):
        conectado =  not self.impresionStatus.conectando
        desempaquetando = not self.impresionStatus.desempaquetando
        instanciando = not self.impresionStatus.instanciando
        imprimiendo = self.impresionStatus.imprimiendo
        marcando = not self.impresionStatus.marcando
        boletas = self.impresionStatus.boletas == []
        instancias = self.impresionStatus.instancias > 0
        instancias_tickets = self.impresionStatus.instancias_tickets >= 0
        impresiones = self.impresionStatus.impresiones >= 0
        marcas = self.impresionStatus.marcas > 0
        
        return  conectado and desempaquetando and instanciando and imprimiendo and marcando and boletas and instancias and instancias_tickets and impresiones and marcas



class Ticket(Observador):
    ''' 
    Esta clase se encarga de manejar los tickets. 
    Observa el estado de impresión y mantiene una lista de comandos.
    '''
    def __init__(self, impresionStatus, sublista):
        ''' 
        Inicializa el ticket. 
        Toma un estado de impresión y una sublista de comandos como argumentos.
        '''
        super().__init__(impresionStatus)
        self.comandos = sublista
        self.impreso = False
        
    def imprimir(self):
        ''' 
        Imprime el ticket. 
        Chequea el puerto, envía los comandos al manejador de respuesta fiscal,
        obtiene los mensajes de estado y cierra el puerto.
        '''
        self.impresionStatus.fh.chequear_puerto()

        for comando in self.comandos:
            bucle = True
            while bucle:
                respuesta = self.impresionStatus.fh.enviar_comando(comando)
                if respuesta == '' or respuesta == None:
                    print("conecte la impresora")
                    bucle = True
                    continue
                else:
                    fiscalResponseHandler = FiscalResponseHandler(comando, respuesta)
                    fiscalResponseHandler.get_mensages_status()
                    bucle = False
        self.impresionStatus.fh.cerrar_puerto()
        time.sleep(2)
        self.impreso = True

    