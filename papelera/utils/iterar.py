from .imprimir_log import imprimir_log_txt
from utils.dicts_to_bin import dict_to_bin, dict_to_int

def iterar(valor_bin_status, status_dic, texto):
    
    status_dic = dict_to_bin(status_dic)
    valor_bin_status = bin(valor_bin_status)[2:]
    
    # Asegúrate de que ambas cadenas tengan la misma longitud
    valor_bin_status = valor_bin_status.zfill(max(len(valor_bin_status), max(len(k) for k in status_dic.keys())))
    
    for k, v in status_dic.items():
        k_bin = k.zfill(len(valor_bin_status))
        
        # Compara los bits de las cadenas
        for i in range(len(valor_bin_status)):
            if valor_bin_status[i] == '1' and k_bin[i] == '1':
                print("iterar log")
                imprimir_log_txt("Estado {}: {}".format(texto,v),"log_corregido.txt")

def iterar_aux(valor_hex_menos_significativo, valor_hex_mas_significativos, status_dic, status_dic_ms, texto, texto_msb):
    status_dic = dict_to_int(status_dic)
    
    for k, v in status_dic.items():
        if valor_hex_menos_significativo == k:
            print("iterar_aux log")
            imprimir_log_txt("Estado {}: {}".format(texto,v),"log_corregido.txt")
            
    for k, v in status_dic_ms.items():
        if valor_hex_mas_significativos == k:
            imprimir_log_txt("Estado {}: {}".format(texto_msb,v),"log_corregido.txt")

def iterar_doc(digito_hex_menos_significativo, digitos_hex_mas_significativos, status_dic, texto):
    status_dic = dict_to_int(status_dic)
    
    if digito_hex_menos_significativo == 1:
        print("iterar_doc log")
        imprimir_log_txt("Estado {}: doc anterior cancelado".format(texto),"log_corregido.txt")
    
    for k, v in status_dic.items():
        if digitos_hex_mas_significativos == k:
            print("iterar_doc log")
            imprimir_log_txt("Estado {}: {}".format(texto,v),"log_corregido.txt")
    