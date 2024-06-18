

from gestor_impresora_fiscal.estado.observers import Observador


class Desempaquetador(Observador):
    ''' 
    Esta clase se encarga de desempaquetar las boletas en formato JSON. 
    Observa el estado de impresión y mantiene un diccionario de boletas.
    '''
    def __init__(self, impresionStatus):
        ''' 
        Inicializa el desempaquetador. 
        Toma un estado de impresión como argumento.
        '''
        super().__init__(impresionStatus)
        self.cantidad_instancias = 0
        self.cantidad_marcas = 0
        
    def instanciarBoletasJson(self):
        ''' 
        Instancia las boletas en formato JSON. 
        Recorre las boletas en el estado de impresión y las instancia como objetos BoletaJson.
        Actualiza la cantidad de instancias y marcas y se vacian las boletas.
        '''
        for boleta in self.impresionStatus.boletas:
            self.impresionStatus.boletas_json[str(boleta["id_boleta"])] = BoletaJson(self.impresionStatus, boleta)
            self.impresionStatus.incrementar_instancias(1)
            self.impresionStatus.incrementar_marcas(1)
        self.impresionStatus.resetear_boletas()
        
    def actualizar(self):
        if self.habilitado():
            self.instanciarBoletasJson()
        
    def habilitado(self):
        conectado =  not self.impresionStatus.conectando
        desempaquetando = self.impresionStatus.desempaquetando
        instanciando = not self.impresionStatus.instanciando
        imprimiendo = not self.impresionStatus.imprimiendo
        marcando = not self.impresionStatus.marcando
        boletas = self.impresionStatus.boletas != []
        instancias = self.impresionStatus.instancias == 0
        impresiones = self.impresionStatus.impresiones == 0
        instancias_tickets = self.impresionStatus.instancias_tickets == 0
        marcas = self.impresionStatus.marcas == 0
        
        return  conectado and desempaquetando and instanciando and imprimiendo and marcando and boletas and instancias and instancias_tickets and impresiones and marcas
 