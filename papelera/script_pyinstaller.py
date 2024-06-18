import ctypes
import urllib.request
import time
import json
import logging

# Configura el logging para escribir en un archivo 'log.txt'
logging.basicConfig(filename='log.txt', level=logging.ERROR)

# Carga la DLL en memoria.
try:
    dll = ctypes.WinDLL('winfis32.dll')
except:
    dll = ctypes.WinDLL(r'//CAJA/Documentos c/py_pyinstaller/winfis32.dll')
# Configura el prototipo y los parámetros para la llamada a la función deseada.
OpenComFiscal = dll.OpenComFiscal
OpenComFiscal.argtypes = [ctypes.c_int, ctypes.c_int]
OpenComFiscal.restype = ctypes.c_int

CloseComFiscal = dll.CloseComFiscal
CloseComFiscal.argtypes = [ctypes.c_int]
CloseComFiscal.restype = None

MandaPaqueteFiscal = dll.MandaPaqueteFiscal
MandaPaqueteFiscal.argtypes = [ctypes.c_int, ctypes.c_char_p]
MandaPaqueteFiscal.restype = ctypes.c_int

UltimaRespuesta = dll.UltimaRespuesta
UltimaRespuesta.argtypes = [ctypes.c_int, ctypes.c_char_p]
UltimaRespuesta.restype = ctypes.c_int

VersionDLLFiscal = dll.VersionDLLFiscal
VersionDLLFiscal.argtypes = []
VersionDLLFiscal.restype = ctypes.c_int

UltimoStatus = dll.UltimoStatus
UltimoStatus.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]
UltimoStatus.restype = ctypes.c_int


def main():
    

    urls = [
        "http://192.168.1.104:8000/boletas_pendientes/",
    ]
    bucle = True
    while bucle:
        for url in urls:
            print(url)
            try:
                response = urllib.request.urlopen(url)
                responseBody = response.read().decode('utf-8')
                print(responseBody)
                break
            except urllib.error.HTTPError as e:
                print("Error: {}".format(e))
                logging.error(e)
                continue

        buffer = ctypes.create_string_buffer(500)

        # Parsea el JSON
        json_response = json.loads(responseBody)
        print(json_response)
        if json_response["boletas"] == []:
            time.sleep(2)
            continue
        else:
            puertoOcupado = True
            while puertoOcupado:
                # Abre la impresora fiscal
                handler = OpenComFiscal(1, 1)
                if handler == -5 or handler == "-5":
                    print("\\nOpenComFiscal retorna {}\\n\\n".format(handler))
                    print("Puerto Ocupado")
                    time.sleep(2)
                else:
                    print("\\nOpenComFiscal retorna {}\\n\\n".format(handler))
                    puertoOcupado = False

            if handler < 0:
                
                print("\\nError OpenComFiscal...FIN !!\\n\\n")
                CloseComFiscal(handler)
                print('Puerto cerrado')
                exit()
                
                
                
                
                
            # cargar boletas ----------------------
            
            boletas = json_response["boletas"]
            VersionDLLFiscal()
            UltimaRespuesta(handler, buffer)

            # Lista de respuestas esperadas
            respuestas_esperadas = ["C080\x1c3600",]

            for boleta in boletas:
                id_boleta = boleta["id_boleta"]
                print(id_boleta)
                comandos = boleta["comandos"]
                
                
                for comando in comandos:
                    comandoStr = comando["comando__comando"]
                    print(comandoStr)
                    
                    print("Comando : {}\\n\\n".format(comandoStr))
                    # Por cada comando en comandos hacer...
                    MandaPaqueteFiscal(handler, comandoStr.encode('utf-8'))
                    time.sleep(1)  # Espera un segundo
                    UltimaRespuesta(handler, buffer)
                    respuesta = buffer.value.decode('utf-8')
                    print("Respuesta : {}\\n\\n".format(respuesta))
                    '''

                    # Si la respuesta no contiene ninguna de las cadenas esperadas, cancelar y salir del bucle
                    if not any(respuesta_esperada in respuesta for respuesta_esperada in respuestas_esperadas):
                        comandoCancelar = chr(152)  # ÿ
                        MandaPaqueteFiscal(handler, comandoCancelar.encode('utf-8'))
                        logging.error(comandoStr)
                        logging.error('Error: la respuesta no contiene ninguna de las cadenas esperadas. Se canceló el proceso.')
                        logging.error(respuesta)
                        break
                    else:
                        logging.error(comandoStr)
                        logging.error(respuesta)
                        '''
                try:
                    data = {
                        'status':'2',
                        'id_boleta':str(id_boleta)
                    }
                    data = json.dumps(data).encode('utf-8')
                    print(data)
                    req = urllib.request.Request(url, data=data, method='POST')
                    req.add_header('Content-Type', 'application/json')
                    
                    with urllib.request.urlopen(req) as f:
                        print('Decode:')
                        print(f.read().decode('utf-8'))
                except Exception as e:
                    print("Error En Post: {}".format(e))
                    logging.error(e)
                    
                    continue
                
                
                
            # Espera un tiempo antes de la próxima solicitud
            CloseComFiscal(handler)
            print('Puerto cerrado')
            time.sleep(10)
            
            #bucle = False

if __name__ == "__main__":
    main()
