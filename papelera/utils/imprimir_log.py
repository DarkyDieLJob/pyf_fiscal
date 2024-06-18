def imprimir_log_txt(data, nombre_archivo):
    # Abre el archivo en modo de escritura
    with open(nombre_archivo, "a") as file:
        # Escribe el texto en el archivo
        print(str(data), file=file)