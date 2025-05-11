import os
import csv
import boto3
import psycopg2
import tempfile
from datetime import datetime
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S' 
)
logger = logging.getLogger('ingesta-gestion')

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'postgres'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'port': os.environ.get('DB_PORT', '5432'),
}

# Configuración de AWS S3
S3_BUCKET = 'proy-cloud-bucket'
S3_PREFIX = 'Gestion'
TIMESTAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 


def connect_to_db():
    """Establece conexión con la base de datos PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Conexión a PostgreSQL establecida correctamente")
        return conn
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL: {e}")
        raise





def extract_data(conn, table_name, columns):
    """Extrae datos de una tabla específica"""
    try:
        cursor = conn.cursor()
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        logger.info(f"Ejecutando consulta: {query}")
        cursor.execute(query)
        data = cursor.fetchall()
        logger.info(f"Se extrajeron {len(data)} registros de la tabla {table_name}")
        return data
    except Exception as e:
        logger.error(f"Error al extraer datos de {table_name}: {e}")
        raise




def format_data_for_csv(data, columns):
    """
    Formatea los datos para CSV, asegurándose de que las fechas tengan el formato correcto
    """
    formatted_data = []
    
    for row in data:
        formatted_row = []
        for i, value in enumerate(row):
            # Si es un objeto datetime, formatearlo según el estándar
            if isinstance(value, datetime):
                formatted_row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                formatted_row.append(value)
        formatted_data.append(formatted_row)
    
    return formatted_data




def save_to_csv(data, columns, file_path):
    """Guarda los datos en un archivo CSV"""
    try:
        # Formatear datos para asegurar que las fechas tengan el formato correcto
        formatted_data = format_data_for_csv(data, columns)
        
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Escribir encabezados
            csv_writer.writerow(columns)
            # Escribir datos
            csv_writer.writerows(formatted_data)
        logger.info(f"Datos guardados correctamente en {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error al guardar en CSV: {e}")
        raise





def upload_to_s3(file_path, s3_key):
    """Sube el archivo CSV a S3"""
    try:
        # Usa las credenciales de ~/.aws/credentials
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)
        logger.info(f"Archivo subido correctamente a s3://{S3_BUCKET}/{s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error al subir a S3: {e}")
        raise




def process_table(conn, table_name, db_columns, file_columns=None):
    """Procesa una tabla completa: extrae, guarda en CSV y sube a S3"""
    try:
        # Si no se especifican columnas para el archivo, usar las mismas de la base de datos
        if file_columns is None:
            file_columns = db_columns
            
        # Extraer datos
        data = extract_data(conn, table_name, db_columns)
        
        # Crear archivo temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        temp_file.close()
        
        # Guardar en CSV
        save_to_csv(data, file_columns, temp_file.name)
        
        # Subir a S3
        s3_key = f"{S3_PREFIX}/{table_name}.csv"
        upload_to_s3(temp_file.name, s3_key)
        
        # Eliminar archivo temporal
        os.unlink(temp_file.name)
        
        logger.info(f"Procesamiento de {table_name} completado con éxito")
    except Exception as e:
        logger.error(f"Error procesando {table_name}: {e}")
        raise







def main():
    """Función principal"""
    try:
        logger.info("Iniciando proceso de ingesta de datos de PostgreSQL a S3")
        
        # Establecer conexión con la base de datos
        conn = connect_to_db()
        
        # Definir mapeo de tablas y columnas
        tables_config = {
            'categoria': {
                'db_columns': ['id', 'name', 'description', 'created_at'],
                'file_columns': ['id', 'nombre', 'descripcion', 'fecha_creacion']
            },
            'producto': {
                'db_columns': ['id', 'name', 'description', 'categoria_id', 'current_stock', 'created_at', 'updated_at'],
                'file_columns': ['id', 'nombre', 'descripcion', 'categoria_id', 'stock_actual', 'fecha_creacion', 'fecha_actualizacion']
            },
            'movimiento_inventario': {
                'db_columns': ['id', 'producto_id', 'type', 'quantity', 'date', 'user_id'],
                'file_columns': ['id', 'producto_id', 'tipo', 'cantidad', 'fecha', 'usuario_id']
            }
        }
        
        # Procesar cada tabla
        for table_name, config in tables_config.items():
            process_table(
                conn, 
                table_name, 
                config['db_columns'],
                config['file_columns']
            )
        
        # Cerrar conexión
        conn.close()
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en el proceso principal: {e}")
        exit(1)

if __name__ == "__main__":
    main()
