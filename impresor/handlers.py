import ctypes
import json
import logging
import time

from impresor.observers import Observador
import urllib.request


class FiscalHandler(Observador):
    def __init__(self, impresionStatus):
        super().__init__(impresionStatus)
        # Carga la DLL en memoria.
        try:
            self.dll = ctypes.WinDLL('C:/Users/Programar/Documents/GitHub/pagina_pf_paoli/smh_p_441f/winfis32.dll')
        except:
            self.dll = ctypes.WinDLL(r'//CAJA/Documentos c/py_pyinstaller/smh_p_441f/winfis32.dll')
        # Configura el prototipo y los parámetros para la llamada a la función deseada.
        self.OpenComFiscal = self.dll.OpenComFiscal
        self.OpenComFiscal.argtypes = [ctypes.c_int, ctypes.c_int]
        self.OpenComFiscal.restype = ctypes.c_int

        self.CloseComFiscal = self.dll.CloseComFiscal
        self.CloseComFiscal.argtypes = [ctypes.c_int]
        self.CloseComFiscal.restype = None

        self.MandaPaqueteFiscal = self.dll.MandaPaqueteFiscal
        self.MandaPaqueteFiscal.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.MandaPaqueteFiscal.restype = ctypes.c_int

        self.UltimaRespuesta = self.dll.UltimaRespuesta
        self.UltimaRespuesta.argtypes = [ctypes.c_int, ctypes.c_char_p]
        self.UltimaRespuesta.restype = ctypes.c_int

        self.VersionDLLFiscal = self.dll.VersionDLLFiscal
        self.VersionDLLFiscal.argtypes = []
        self.VersionDLLFiscal.restype = ctypes.c_int

        self.UltimoStatus = self.dll.UltimoStatus
        self.UltimoStatus.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]
        self.UltimoStatus.restype = ctypes.c_int

        
        self.buffer = ctypes.create_string_buffer(500)
        
        self.handler = None
        
    def chequear_puerto(self):
        self.impresionStatus.com_ocupado = True
        self.impresionStatus.com_abierto = False
        while self.impresionStatus.com_ocupado:
            # Abre la impresora fiscal
            self.handler = self.OpenComFiscal(1, 1)
            
            if self.handler < 0 :
                if self.handler == -5 or self.handler == "-5":
                    print("\\nOpenComFiscal retorna {}\\n\\n".format(self.handler))
                    print("Puerto Ocupado")
                    time.sleep(2)
                    self.impresionStatus.com_ocupado = True
                else:
                    print("\\nError OpenComFiscal...FIN !!\\n\\n")
                    self.CloseComFiscal(self.handler)
                    print('Puerto cerrado')
                    self.impresionStatus.com_abierto = False
            else:
                print("\\nOpenComFiscal retorna {}\\n\\n".format(self.handler))
                self.impresionStatus.com_ocupado = False

    def cerrar_puerto(self):
        # Espera un tiempo antes de la próxima solicitud
        self.CloseComFiscal(self.handler)
        print('Puerto cerrado')
        self.puerto_abierto = False
        self.puerto_ocupado = True
        time.sleep(2)
    
    def capturar_ultima_respuesta(self):
        self.UltimaRespuesta(self.handler, self.buffer)
        respuesta = self.buffer.value.decode('utf-8')
        return respuesta
    
    def enviar_comando(self, comando):
        
        self.MandaPaqueteFiscal(self.handler, comando.encode('utf-8'))
        time.sleep(1)  # Espera un segundo
        
        return self.capturar_ultima_respuesta()

class ConectionHandler(Observador):
    ''' 
    Esta clase se encarga de manejar las conexiones con una API. 
    Observa el estado de impresión y mantiene una lista de boletas pendientes.
    '''
    def __init__(self, impresionStatus):
        ''' 
        Inicializa el manejador de conexiones. 
        Toma un estado de impresión como argumento.
        '''
        super().__init__(impresionStatus)
        self.boletas = []
        self.url = "http://192.168.0.15:8000/boletas_pendientes/"
        self._url_response = None
        self._responseBody = None
        self._json_response = None
        
        self.conected = False
        self.boletas_disponibles = False
        
    def _chequear_url(self):
        ''' 
        Chequea la URL de la API. 
        Si la URL es accesible, establece la conexión como True.
        '''
        try:
            self._url_response = urllib.request.urlopen(self.url)
            self.conected = True
            
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print("Error: {}".format(e))
            self.conected = False
            
    def _capturar_respuesta(self):
        ''' 
        Captura la respuesta de la API. 
        Si la conexión es exitosa, lee la respuesta y la carga como un objeto JSON.
        '''
        self._chequear_url()
        if self.conected:
            try:
                self._responseBody = self._url_response.read().decode('utf-8')
                self._json_response = json.loads(self._responseBody)
                if self._json_response["boletas"] == []:
                    self.boletas_disponibles = False
                    time.sleep(5)
                else:
                    self.boletas_disponibles = True
                    
                    self.boletas = self._json_response["boletas"]
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print("Error: {}".format(e))
                logging.error(e)
                self.conected = False
    
    def conectar_api_get(self):
        ''' 
        Conecta con la API y obtiene las boletas pendientes. 
        Continúa intentando hasta que haya boletas disponibles.
        '''
        while not self.boletas_disponibles:
            self._capturar_respuesta()
            if self.boletas != []:
                self.conected = False
                self.impresionStatus.boletas = self.boletas
            else:
                self.conected = True
    
    def marcar_impreso(self, id_boleta):
        '''No modifica...'''
        marcado = False
        self.conected = False
        while not marcado:
            while not self.conected:
                self._chequear_url()
            if self.conected:
                try:
                    data = {
                        'status':'2',
                        'id_boleta':str(id_boleta)
                    }
                    data = json.dumps(data).encode('utf-8')
                    req = urllib.request.Request(self.url, data=data, method='POST')
                    req.add_header('Content-Type', 'application/json')
                    
                    with urllib.request.urlopen(req) as f:
                        #print('Decode:')
                        #print(f.read().decode('utf-8'))
                        pass
                    marcado = True
                    self.conected = False
                    
                except Exception as e:
                    print("Error En Post: {}".format(e))
                    logging.error(e)
                
    def actualizar(self):
        if self.habilitado():
            self.conectar_api_get()
        if self.habilitado_marcado():
            print("Habilitado : para marcar....")
            for id in self.impresionStatus.id_boletas:
                print("id: ",id)
                self.marcar_impreso(id)
                self.impresionStatus.decrementar_marca(1)
            self.impresionStatus.resetear_atributos()
            self.boletas_disponibles = False
    
    def habilitado(self):
        conectado = self.impresionStatus.conectando
        desempaquetando = not self.impresionStatus.desempaquetando
        instanciando = not self.impresionStatus.instanciando
        imprimiendo = not self.impresionStatus.imprimiendo
        marcando = not self.impresionStatus.marcando
        boletas = self.impresionStatus.boletas == []
        instancias = self.impresionStatus.instancias == 0
        impresiones = self.impresionStatus.impresiones == 0
        instancias_tickets = self.impresionStatus.instancias_tickets == 0
        marcas = self.impresionStatus.marcas >= 0
        
        return  conectado and desempaquetando and instanciando and imprimiendo and marcando and boletas and instancias and instancias_tickets and impresiones and marcas
    
    def habilitado_marcado(self):
        conectado = self.impresionStatus.conectando
        desempaquetando = not self.impresionStatus.desempaquetando
        instanciando = not self.impresionStatus.instanciando
        imprimiendo = not self.impresionStatus.imprimiendo
        marcando = self.impresionStatus.marcando
        boletas = self.impresionStatus.boletas == []
        instancias = self.impresionStatus.instancias == 0
        impresiones = self.impresionStatus.impresiones == 0
        instancias_tickets = self.impresionStatus.instancias_tickets == 0
        marcas = self.impresionStatus.marcas >= 0
        
        return  conectado and desempaquetando and instanciando and imprimiendo and marcando and boletas and instancias and instancias_tickets and impresiones and marcas
    