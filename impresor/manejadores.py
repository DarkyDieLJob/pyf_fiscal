from impresor.handlers import FiscalHandler


class ImpresionStatus:
    def __init__(self):
        self._observadores = []
        self._observadores_base = []
        self.fh = FiscalHandler(self)
        self.resetear_atributos()
        self.status = {}
        self.boletas_json = {}
    
    def resetear_atributos(self):
        self._observadores = self._observadores_base
        self.conectando = False
        self.desempaquetando = False
        self.instanciando = False
        self.imprimiendo = False
        self.marcando = False
        self.instancias = 0
        self.instancias_tickets = 0
        self.impresiones = 0
        self.marcas = 0
        self.boletas = []
    
        
    def get_status(self):
        self.status = {
            'conectando': self.conectando,
            'desempaquetando': self.desempaquetando,
            'instanciando': self.instanciando,
            'imprimiendo': self.imprimiendo,
            'marcando': self.marcando,
            'instancias': self.instancias,
            'instancias_tickets': self.instancias_tickets,
            'impresiones': self.impresiones,
            'marcas': self.marcas,
            'boletas': self.boletas
        }
        return self.status


    def establecer_conectando(self, boleando):
        self.conectando = boleando
        
    def incrementar_instancias(self, cantidad):
        self.instancias += cantidad
        
    def incrementar_marcas(self, cantidad):
        self.marcas += cantidad
        
    def incrementar_instancias_tickets(self, cantidad):
        self.instancias_tickets += cantidad
        self.impresiones += cantidad
        
    def decrementar_impresiones(self, cantidad):
        self.impresiones -= cantidad
        
    def decrementar_instancia_tickets(self, cantidad):
        self.instancias_tickets -= cantidad
    
    def decrementar_instancia(self, cantidad, boleta_json):
        self.instancias -= cantidad
        if boleta_json in self._observadores:
            self.remover_observador(boleta_json)
        if boleta_json.id_boleta in self.boletas_json:
            del self.boletas_json[boleta_json.id_boleta]

        
    def decrementar_marca(self, cantidad):
        self.marcas -= cantidad
        
    def resetear_boletas(self):
        self.id_boletas = [boleta['id_boleta'] for boleta in self.boletas]
        print(self.id_boletas)
        self.boletas = []
        
        
    def agregar_observador(self, observador):
        self._observadores.append(observador)

    def notificar_todos_observadores(self):
        print(self.get_status())
        for observador in self._observadores:
            observador.actualizar()
            
    def remover_observador(self, observador):
        self._observadores.remove(observador)

    def conectar(self):
        if not self.conectando:  # Solo se puede conectar si no está conectado
            self.conectando = True
            self.notificar_todos_observadores()
            
    def desempaquetar(self):
        if self.conectando:  # Solo se puede desempaquetar si está conectado
            self.conectando = False
            self.desempaquetando = True
            self.notificar_todos_observadores()

    def instanciar(self):
        if self.desempaquetando and self.instancias > 0:  # Solo se puede instanciar si está desempaquetado y hay instancias pendientes
            self.desempaquetando = False
            self.instanciando = True
            self.notificar_todos_observadores()

    def imprimir(self):
        if self.instanciando and self.impresiones > 0:  # Solo se puede imprimir si está instanciado y hay impresiones pendientes
            self.instanciando = False
            self.imprimiendo = True
            self.notificar_todos_observadores()

    def marcar(self):
        if self.imprimiendo and self.marcas > 0:  # Solo se puede marcar si se ha impreso y hay marcas pendientes
            self.imprimiendo = False
            self.conectando = True
            self.marcando = True
            self.notificar_todos_observadores()
