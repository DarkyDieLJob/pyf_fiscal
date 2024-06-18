from status_codes.auxiliar_status_code import auxiliar_status_codes
from status_codes.auxiliar_status_code_msb import auxiliar_status_codes_msb
from status_codes.document_status_code import document_status_codes
from status_codes.fiscal_status_code import fiscal_status_codes
from status_codes.printer_status_code import printer_status_codes

from catch_status_codes.listar_comandos import comandos_art_bdd

from utils.iterar import iterar, iterar_aux, iterar_doc
from utils.imprimir_log import imprimir_log_txt

class FiscalResponseHandler():    
    
    def __init__(self, comando, respuesta) -> None:
        self.comando = comando[0]
        self.parametros = respuesta
        self.valor_status_impresora = int(self.parametros[0], 16)
        self.valor_status_fiscal = int(self.parametros[1], 16)
        
        self.p_auxiliar = -1
        self.p_document = -1
        dict = next((item for item in comandos_art_bdd if comando[0] in item), None)
        if dict:
            p = dict[comando[0]]
            self.p_auxiliar = int(p["auxiliar_status"])
            self.p_document = int(p["document_status"])
    
    
    
    def get_mensages_impresora(self):
        iterar(
            self.valor_status_impresora, 
            printer_status_codes, 
            "de la impresora---"
            )
    
    def get_mensages_fiscal(self):
        iterar(
            self.valor_status_fiscal, 
            fiscal_status_codes, 
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
                auxiliar_status_codes, 
                auxiliar_status_codes_msb,
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
                document_status_codes,
                "del documento-----"
                )
    
    def get_mensages_status(self):
        self.get_mensages_impresora()
        self.get_mensages_fiscal()
        self.get_mensages_auxiliar()
        self.get_mensages_document()
    
    

def main ():
    nombre_archivo = "log.txt"
    
    def procesar_log(nombre_archivo):
        nuevo_archivo = []

        with open(nombre_archivo, 'r') as archivo:
            lineas = archivo.readlines()

        for linea in lineas:
            if "la respuesta no contiene ninguna de las cadenas esperadas" not in linea:
                nuevo_archivo.append(linea)

        for i in range(0, len(nuevo_archivo), 2):  # Comenzamos desde 1 y saltamos de dos en dos
            if "ERROR:root:" in nuevo_archivo[i]:
                comando = nuevo_archivo[i-1].split("ERROR:root:")[1].strip()
                comando = comando.split('\x1c')
                
                respuesta = nuevo_archivo[i].split("ERROR:root:")[1].strip()
                respuesta = respuesta.split('\x1c')
                print("ingresantes")
                print("comando: ",comando)
                print("respuesta: ",respuesta)
                
                respuesta_fiscal = FiscalResponseHandler(comando, respuesta)
                if comando[0] == "*":
                    imprimir_log_txt("\n","log_corregido.txt")
                    imprimir_log_txt("--------  STATUS  --------","log_corregido.txt")
                    
                elif comando[0] == "@":
                    imprimir_log_txt("\n","log_corregido.txt")
                    imprimir_log_txt("--------  NUEVO   --------","log_corregido.txt")
                
                else:
                    imprimir_log_txt("Comando------------------: '{}'".format(comando[0]),"log_corregido.txt")
                respuesta_fiscal.get_mensages_status()
                    

                    

    procesar_log(nombre_archivo)



if __name__ == "__main__":
    main()