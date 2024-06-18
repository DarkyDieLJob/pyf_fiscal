

class Observador:
    def __init__(self, impresionStatus):
        self.impresionStatus = impresionStatus
        self.impresionStatus.agregar_observador(self)
        

    def actualizar(self):
        pass

    def habilitado(self, accion):
        pass