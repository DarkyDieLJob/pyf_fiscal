from os import error
from core_dir.core import FiscalResponseHandler

import ctypes
import urllib.request
import time
import json
import logging

import traceback



class ImpresionStatus():
    def __init__(self):
        self._observadores = set()
        
        self.fh = FiscalHandler(self)

        self.conected = False
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = False
        
        self.com_ocupado = False
        self.com_abierto = False
        
        self.imprimiendo = False
        self.impreso = False
        
        self.marcado = False
         
    def imprimir_estado_interno(self, text="None", e="Safe"):
        print("##############################################")
        print(text)
        print("----------------------------------------------")
        print("----------------------------------------------")
        print("conected: ",self.conected)
        print("----------------------------------------------")
        print("boletas_disponibles: ",self.boletas_disponibles)
        print("desempaquetando: ",self.desempaquetando)
        print("instanciando: ",self.instanciando)
        print("----------------------------------------------")
        print("com ocupado: ",self.com_ocupado)
        print("com abierto: ",self.com_abierto)
        print("----------------------------------------------")
        print("imprimiendo: ",self.imprimiendo)
        print("impreso: ",self.impreso)
        print("----------------------------------------------")
        print("marcado: ",self.marcado)
        print("----------------------------------------------")
        print("----------------------------------------------")
        print("FiscalHandler: ",self.fh)
        print("----------------------------------------------")
        print("Error: ", e)
        traceback.print_exc()
        print("##############################################")
        print("")
        
    def registrar_observador(self, observador):
        self._observadores.add(observador)
    
    def notificar_observadores(self):
        for observador in self._observadores:
            observador.actualizar()
    
    def coneccion_exitosa(self):
        self.conected = True
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = False
        
        self.com_ocupado = False
        self.com_abierto = False
        
        self.imprimiendo = False
        self.impreso = False
        
        self.marcado = False
        
    def instanciado_exitoso(self):
        self.conected = False
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = True
        
        self.com_ocupado = False
        self.com_abierto = False
        
        self.imprimiendo = False
        self.impreso = False
        
        self.marcado = False
        
    def impresora_lista(self):
        self.conected = False
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = False
        
        self.com_ocupado = False
        self.com_abierto = True
        
        self.imprimiendo = False
        self.impreso = False
        
        self.marcado = False
        
    def impresion_exitosa(self):
        self.conected = False
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = False
        
        self.com_ocupado = False
        self.com_abierto = False
        
        self.imprimiendo = False
        self.impreso = True
        
        self.marcado = False
    
    def marcado_completado(self):
        self.conected = False
        
        self.boletas_disponibles = False
        self.desempaquetando = False
        self.instanciando = False
        
        self.com_ocupado = False
        self.com_abierto = False
        
        self.imprimiendo = False
        self.impreso = False
        
        self.marcado = True
       
class Observador():
    def __init__(self, impresionStatus):
        self.impresionStatus = impresionStatus

    def conectar_api_get(self):
        pass
    def hay_boletas(self):
        pass
    def desempaquetando(self):
        pass
    def instanciando(self):
        pass
    def imprimiendo(self):
        pass
    def actualizar(self):
        if not self.impresionStatus.conected:
            print("conectando...")
            self.conectar_api_get()
        else:
            print("conectado")
            
                
        if self.impresionStatus.boletas_disponibles:
            print("boletas disponibles")
            self.hay_boletas()
                
        if self.impresionStatus.desempaquetando:
            print("desempaquetando...")
            self.desempaquetando()
                
        if self.impresionStatus.instanciando:
            print("instanciando...")
            self.instanciando()
                
        if self.impresionStatus.imprimiendo:
            print("imprimiendo...")
            self.imprimiendo()
           
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
    def __init__(self, impresionStatus):
        super().__init__(impresionStatus)
        self.boletas = []
        self.url = "http://192.168.1.104:8000/boletas_pendientes/"
        self._url_response = None
        self._responseBody = None
        self._json_response = None
        self.boletas = None
        
    def _chequear_url(self):
        '''Si hay coneccion: \n
        impresionStatus.conected = True'''
        try:
            self._url_response = urllib.request.urlopen(self.url)
            self.impresionStatus.conected = True
            
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            print("Error: {}".format(e))
            self.impresionStatus.conected = False
            
    def _capturar_respuesta(self):
        '''Si impresionStatus.conected -> \n
        Si boletas disponibles: \n
        impresionStatus.boletas_disponibles = True \n
        Si error \n
        impresionStatus.conected = False'''
        self._chequear_url()
        if self.impresionStatus.conected:
            try:
                self._responseBody = self._url_response.read().decode('utf-8')
                self._json_response = json.loads(self._responseBody)
                if self._json_response["boletas"] == []:
                    self.impresionStatus.boletas_disponibles = False
                    time.sleep(5)
                else:
                    self.impresionStatus.boletas_disponibles = True
                    self.boletas = self._json_response["boletas"]
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print("Error: {}".format(e))
                logging.error(e)
                self.impresionStatus.conected = False
    
    def conectar_api_get(self):
        '''Si todo bien: \n
        impresionStatus.boletas_disponibles = True \n
        impresionStatus.conected = True'''
        self._capturar_respuesta()
    
    def marcar_impreso(self, id_boleta):
        '''No modifica...'''
        marcado = False
        while not marcado:
            self._chequear_url()
            if self.impresionStatus.conected:
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
                    
                except Exception as e:
                    print("Error En Post: {}".format(e))
                    logging.error(e)
        
class Desempaquetador(Observador):
    def __init__(self, impresionStatus):
        super().__init__(impresionStatus)
        self.boletas = {}
        
    def instanciarBoletasJson(self, boletas):
        '''Si hay boletas-> \n
        Si boletas disponibles: \n
        impresionStatus.desempaquetando = False \n
        impresionStatus.instanciando = True \n
        Si error: \n
        impresionStatus.desempaquetando = False \n
        impresionStatus.instanciando = False \n'''
        
        if self.impresionStatus.boletas_disponibles:
            for boleta in boletas:
                self.boletas[str(boleta["id_boleta"])] = BoletaJson(self.impresionStatus, boleta)
                self.impresionStatus.desempaquetando = True
            self.impresionStatus.desempaquetando = False
            self.impresionStatus.instanciando = True
        else:
            self.impresionStatus.desempaquetando = False
            self.impresionStatus.instanciando = False
            
class Ticket(Observador):
    def __init__(self, impresionStatus, sublista):
        super().__init__(impresionStatus)
        self.comandos = sublista
        
    def imprimir(self):
        self.impresionStatus.fh.chequear_puerto()

        for comando in self.comandos:
            respuesta = self.impresionStatus.fh.enviar_comando(comando)
            fiscalResponseHandler = FiscalResponseHandler(comando, respuesta)
            fiscalResponseHandler.get_mensages_status()
        self.impresionStatus.fh.cerrar_puerto()
        time.sleep(2)
        
class BoletaJson(Observador):
    def __init__(self, impresionStatus, boleta):
        super().__init__(impresionStatus)
        self.json = boleta
        self.id_boleta = self.json["id_boleta"]
        self.tipo = self.json["tipo"]
        self.comandos = self.json["comandos"]
        self.tickets = {}
        self.instanciar_tickets()
            
    def instanciar_tickets(self):
        '''Cra la instancia de cada ticket asociado a la boleta'''
        self.impresionStatus.desempaquetando = True
        self.impresionStatus.instanciando = True
        sublista = []
        n = 0
        self.tickets = {}
        if self.tipo == "Z":
            self.tickets[str(n)] = Ticket(self.impresionStatus, self.comandos)
        else:
            for comando in self.comandos:
                sublista.append(comando)
                
                if comando == "E":
                    self.tickets[str(n)] = Ticket(self.impresionStatus, sublista)
                    sublista = []
                    n = n+1
                
    def enviar_impresiones(self):
        self.impresionStatus.instanciando = False
        self.impresionStatus.imprimiendo = True
        for id, ticket in self.tickets.items():
            print(ticket)
            print("{}/{}".format(id,len(self.tickets.items())))
            ticket.imprimir()
            
        self.impresionStatus.imprimiendo = False
          
def programa():
    '''Instancia y ejecucion'''
    ists = ImpresionStatus()
    conector = ConectionHandler(ists)
    en_ejecucion = True
    while en_ejecucion:
        try:
            conector.conectar_api_get()
        except Exception as e:
            ists.imprimir_estado_interno("Conectando...", e)
        
        if ists.boletas_disponibles:
            try:
                desempaquetador = Desempaquetador(ists)
                desempaquetador.instanciarBoletasJson(conector.boletas)
            except Exception as e:
                ists.imprimir_estado_interno("Instanciando boletas...", e)
            
            for _, boleta in desempaquetador.boletas.items():
                try:
                    boleta.instanciar_tickets()
                except Exception as e:
                    ists.imprimir_estado_interno("Instanciando tickets...", e)
                
                try:
                    boleta.enviar_impresiones()
                except Exception as e:
                    ists.imprimir_estado_interno("Imprimiendo tickets...", e)
                
                try:
                    conector.marcar_impreso(boleta.id_boleta)
                except Exception as e:
                    ists.imprimir_estado_interno("Marcando boleta como imprimida...", e)
            
            ists.imprimiendo = False
            ists.boletas_disponibles = False
            ists.imprimir_estado_interno("Ciclo completado...")
    
    

import unittest
from unittest.mock import MagicMock, patch

class TestPrograma(unittest.TestCase):
    @patch.object(ImpresionStatus, '__init__', return_value=None)
    @patch.object(ConectionHandler, '__init__', return_value=None)
    @patch.object(Desempaquetador, '__init__', return_value=None)
    def test_programa(self, mock_Desempaquetador, mock_ConectionHandler, mock_ImpresionStatus):
        # Configurar los objetos simulados
        mock_boleta = MagicMock()
        mock_Desempaquetador.return_value.boletas.items.return_value = [(None, mock_boleta)]
        mock_ConectionHandler.return_value.boletas = []

        # Llamar a la función que quieres probar
        programa()

        # Verificar que los métodos se llamaron correctamente
        mock_ImpresionStatus.assert_called_once()
        mock_ConectionHandler.assert_called_once_with(mock_ImpresionStatus.return_value)
        mock_ConectionHandler.return_value.conectar_api_get.assert_called_once()
        mock_Desempaquetador.assert_called_once_with(mock_ImpresionStatus.return_value, mock_ConectionHandler.return_value.boletas)
        mock_Desempaquetador.return_value.instanciarBoletasJson.assert_called_once()
        mock_boleta.instanciar_tickets.assert_called_once()
        mock_boleta.enviar_impresiones.assert_called_once()
        mock_ConectionHandler.return_value.marcar_impreso.assert_called_once_with(mock_boleta.id_boleta)

if __name__ == '__main__':
    programa()
    
 