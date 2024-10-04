# Importamos las librerías necesarias
import os
import argparse
import time

# Librería para darle color a la salida en la terminal
from colorama import Fore

# Librerías para manipulación de PDFs
from PyPDF2 import PdfReader, PdfWriter

def get_parser() -> argparse.ArgumentParser:
    """
    Esta función crea el parser de los argumentos que el programa recibirá.
    Los argumentos son:
        -o, --output: Nombre del archivo de salida. Si no se especifica, será el nombre del primer archivo con "_merged.pdf" al final.
        -r, --remove-ads: Remover los anuncios del PDF.
        -v, --verbose: Modo detallado, muestra más información sobre el proceso.
        -l, --log: Archivo para guardar los registros de las operaciones.
        input: Archivo de entrada (uno o varios).
    :return: Parser de los argumentos.
    """
    parser = argparse.ArgumentParser(
        description="Este programa fusionará los archivos PDF que pases como argumentos en un solo archivo y eliminará los anuncios del PDF si lo deseas.",
        epilog="Este programa fue creado por @DaniFdz",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Argumentos opcionales
    parser.add_argument("-o", "--output", help="Nombre del archivo de salida, si no se especifica será el nombre del primer archivo con _merged.pdf al final", required=False)
    parser.add_argument("-r", "--remove-ads", help="Eliminar los anuncios del PDF", action="store_true")
    parser.add_argument("-v", "--verbose", help="Modo detallado, muestra más información sobre el proceso", action="store_true")
    parser.add_argument("-l", "--log", help="Archivo para guardar los registros de las operaciones", action="store_true")
    # Argumento posicional (uno o más archivos de entrada)
    parser.add_argument("input", help="Archivo de entrada", nargs="+")

    return parser

def check_args(args):
    """
    Esta función verificará si los argumentos recibidos son correctos.
    :param args: Los argumentos que el programa recibió.
    :return: None
    """
    # Si se especifica un archivo de log, verificamos si existe el directorio para guardarlo
    if args.log:
        if args.verbose:
            print(f"{Fore.MAGENTA}[V]{Fore.RESET} Verificando si el archivo de log existe...")

        # Si no existe el directorio "logs", lo creamos
        if not os.path.exists("./logs"):
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Creando el directorio de logs...")
            os.makedirs("./logs")
            os.chmod("./logs", 0o777)  # Permisos de lectura, escritura y ejecución para todos

        # Creamos el archivo de log
        log_file = open(f"./logs/log_{os.getpid()}.txt", "w")
        log_file.write(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] Archivo de log creado")
        log_file.close()

    # Verificamos si el archivo de salida existe
    if args.verbose:
        print(f"{Fore.MAGENTA}[V]{Fore.RESET} Verificando si el archivo de salida existe...")

    # Si no se especifica archivo de salida, se genera uno por defecto
    if args.output is None:
        args.output = "".join(args.input[0].split(".")[:-1]) + "_merged.pdf"

    # Si el archivo de salida ya existe, pedimos confirmación al usuario para sobrescribirlo
    if os.path.exists(args.output):
        if(input(f"El archivo \"{args.output}\" ya existe, ¿deseas sobrescribirlo? [y/N]: ").lower() != "y"):
            print("\nOperación cancelada por el usuario")
            print(Fore.RED + "\tSaliendo..." + Fore.RESET)
            exit(1)

    # Verificamos que todos los archivos de entrada existan
    for file in args.input:
        if args.verbose:
            print(f"{Fore.MAGENTA}[V]{Fore.RESET} Verificando si el archivo {file} existe...")
        if not os.path.exists(file):
            print(f"\nEl archivo {Fore.YELLOW}{file}{Fore.RESET} no existe")
            print(Fore.RED + "\tSaliendo..." + Fore.RESET)
            exit(1)

def main():
    """
    Función principal del programa.
    :return: None
    """
    # Creamos el parser y analizamos los argumentos
    parser = get_parser()
    args = parser.parse_args()

    # Verificamos que los argumentos sean válidos
    check_args(args)
    
    try:
        # Manejo de logging si el usuario lo especifica
        if args.log:
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Abriendo el archivo de log...")
            log_file = open(f"./logs/log_{os.getpid()}.txt", "a+")

        if args.verbose:
            print(f"{Fore.MAGENTA}[V]{Fore.RESET} Abriendo el archivo de salida...")

        # Abrimos el archivo de salida en modo escritura binaria
        with open(args.output, 'wb') as f:
            f.write(b'')  # Inicializamos el archivo vacío

        output_file = open(args.output, "wb")
        writer = PdfWriter()

        if args.verbose:
            print(f"{Fore.MAGENTA}[V]{Fore.RESET} Archivo de salida abierto")
        if args.log:
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Archivo de salida abierto")

        # Procesamos cada archivo de entrada
        for file in args.input:
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Abriendo el archivo de entrada \"{file}\"...")
            input_file = open(file, "rb")
            reader = PdfReader(input_file)

            # Mostramos cuántas páginas tiene el archivo
            if args.verbose:
                print(f"{Fore.YELLOW}[i]{Fore.RESET} Número de páginas en \"{file}\": {len(reader.pages)}")
            
            # Añadimos las páginas al archivo de salida
            for page in reader.pages:
                if page.extract_text() != "":  # Verificamos que la página no esté vacía
                    writer.add_page(page)
            input_file.close()

            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Páginas de \"{file}\" añadidas al archivo de salida")
            if args.log:
                log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Páginas de \"{file}\" añadidas al archivo de salida")
            
        # Cerramos el archivo de salida
        if args.verbose:
            print(f"{Fore.MAGENTA}[V]{Fore.RESET} Cerrando el archivo de salida...")
        if args.log:
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Cerrando el archivo de salida")

        writer.write(output_file)
        output_file.close()

        # Eliminamos los anuncios si el usuario lo especificó
        if args.remove_ads:
            from gulagcleaner.gulagcleaner_extract import deembed
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Eliminando los anuncios del archivo de salida...")
            if args.log:
                log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Eliminando los anuncios del archivo de salida...")
            
            # Llamamos a la función de eliminación de anuncios
            resp = deembed(args.output, True)
            print(resp)  # Imprimir la respuesta para depuración
            if not resp["Success"]:
                print(f"{Fore.RED}Error:{Fore.RESET} {resp['Error']}")
                if args.log:
                    log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Error al eliminar los anuncios")
                    log_file.close()
                exit(1)

        # Finalizamos el archivo de log si es necesario
        if args.log:
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Cerrando el archivo de log...")
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Operación completada con éxito")
            log_file.close()
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Archivo de log cerrado")

        print(f"\n{Fore.YELLOW}Operación completada con éxito{Fore.RESET}")

    # Manejamos la interrupción del usuario
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        print(Fore.RED + "\tSaliendo..." + Fore.RESET)
        if args.log:
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Cerrando el archivo de log...")
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Operación cancelada por el usuario")
            log_file.close()
        exit(1)
    
    except Exception as e:
        print("\nUn error ha ocurrido")
        print(Fore.RED + "\tSaliendo..." + Fore.RESET)
        if args.log:
            if args.verbose:
                print(f"{Fore.MAGENTA}[V]{Fore.RESET} Cerrando el archivo log...")
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Un error ha ocurrido")
            log_file.write(f"\n[{time.strftime('%d/%m/%Y %H:%M:%S')}] Cerrando el archivo log...")
            log_file.close()
        raise e


if __name__ == "__main__":
    main()