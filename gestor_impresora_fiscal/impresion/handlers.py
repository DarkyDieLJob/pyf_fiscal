import ctypes
import time

from estado.observers import Observador

from .utils.iterar_respuesta import iterar, iterar_aux, iterar_doc
from .utils.status_codes.auxiliar_status_code import AUXILIAR_STATUS_CODES
from .utils.status_codes.auxiliar_status_code_msb import AUXILIAR_STATUS_CODES_MSB
from .utils.status_codes.document_status_code import DOCUMENT_STATUS_CODES
from .utils.status_codes.fiscal_status_code import FISCAL_STATUS_CODES
from .utils.status_codes.printer_status_code import PRINTER_STATUS_CODES

from impresion.utils.comandos.listar_comandos import COMANDOS_ART_BDD

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


    
class FiscalResponseHandler():    
    
    def __init__(self, comando, respuesta) -> None:
        self.comando = comando[0]
        self.parametros = respuesta
        self.valor_status_impresora = int(self.parametros[0], 16)
        self.valor_status_fiscal = int(self.parametros[1], 16)
        
        self.p_auxiliar = -1
        self.p_document = -1
        dict = next((item for item in COMANDOS_ART_BDD if comando[0] in item), None)
        if dict:
            p = dict[comando[0]]
            self.p_auxiliar = int(p["auxiliar_status"])
            self.p_document = int(p["document_status"])
    
    
    
    def get_mensages_impresora(self):
        iterar(
            self.valor_status_impresora, 
            PRINTER_STATUS_CODES, 
            "de la impresora---"
            )
    
    def get_mensages_fiscal(self):
        iterar(
            self.valor_status_fiscal, 
            FISCAL_STATUS_CODES, 
            "fiscal------------"
            )
    
    def get_mensages_auxiliar(self):
        if self.p_auxiliar >= 0:
            valor_status_auxiliar = self.parametros[self.p_auxiliar]
            
            digito_hex_menos_significativo = valor_status_auxiliar[-1]
            digito_hex_mas_significativo = valor_status_auxiliar[:1]
            
            valor_hex_menos_significativo = int(digito_hex_menos_significativo, 16)
            valor_hex_mas_significativo = int(digito_hex_mas_significativo, 16)
            iterar_aux(
                valor_hex_menos_significativo, 
                valor_hex_mas_significativo,
                AUXILIAR_STATUS_CODES, 
                AUXILIAR_STATUS_CODES_MSB,
                "auxiliar----------",
                "auxiliar-msb------"
                )
    
    def get_mensages_document(self):
        if self.p_document >= 0:
            valor_status_documento = self.parametros[self.p_document]
            
            digito_hex_menos_significativo = valor_status_documento[-1]
            digitos_hex_mas_significativos = valor_status_documento[:2]
            
            valor_hex_menos_significativo = int(digito_hex_menos_significativo, 16)
            valor_hex_mas_significativo = int(digitos_hex_mas_significativos, 16)
            
            iterar_doc(
                valor_hex_menos_significativo, 
                valor_hex_mas_significativo, 
                DOCUMENT_STATUS_CODES,
                "del documento-----"
                )
    
    def get_mensages_status(self):
        self.get_mensages_impresora()
        self.get_mensages_fiscal()
        self.get_mensages_auxiliar()
        self.get_mensages_document()
    
