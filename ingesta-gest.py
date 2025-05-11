import boto3
import psycopg2
import csv
from psycopg2 import sql
import os

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'tarea-db'),
    'port': int(os.getenv('DB_PORT', '5432'))
}

nombreBucket = "tarea-ingesta02"
ficheroCSV = "movimiento_inventario.csv"
tabla_a_exportar = "movimiento_inventario"

def exportar_tabla_a_csv():
    try:
        print("Conectando a PostgreSQL...")
        conexion = psycopg2.connect(**db_config)
        cursor = conexion.cursor()
        
        print(f"Exportando datos de la tabla {tabla_a_exportar}...")
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(tabla_a_exportar))
        cursor.execute(query)
        resultados = cursor.fetchall()
        
        if not resultados:
            print("La tabla está vacía")
            return False
        
        # Escribir a CSV
        with open(ficheroCSV, 'w', newline='') as archivo_csv:
            writer = csv.writer(archivo_csv)
            writer.writerows(resultados)
        
        print(f"Datos exportados correctamente a {ficheroCSV}")
        return True
        
    except Exception as e:
        print(f"Error al exportar datos: {e}")
        return False
    finally:
        if 'conexion' in locals() and not conexion.closed:
            cursor.close()
            conexion.close()

def subir_a_s3():
    try:
        print("Conectando a S3...")
        s3 = boto3.client('s3')
        s3.upload_file(ficheroCSV, nombreBucket, ficheroCSV)
        print(f"Archivo {ficheroCSV} subido correctamente a S3 en el bucket {nombreBucket}")
        return True
    except Exception as e:
        print(f"Error al subir a S3: {e}")
        return False

if __name__ == "__main__":
    print("=== Iniciando proceso de ingesta ===")
    if exportar_tabla_a_csv():
        if subir_a_s3():
            print("Proceso completado exitosamente")
        else:
            print("Error en la subida a S3")
    else:
        print("Error en la exportación de datos")
