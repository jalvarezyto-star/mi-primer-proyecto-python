import csv
import mysql.connector
from mysql.connector import Error

def ejecutar_etl():
    # Contadores para el reporte obligatorio por consola
    registros_exitosos = 0
    registros_descartados = 0
    
    # -------------------------------------------------------------------------
    # 1. CONEXIÓN Y PREPARACIÓN DE LA BASE DE DATOS
    # -------------------------------------------------------------------------
    try:
        # Conexión inicial al servidor MySQL local para asegurar la base de datos
        conexion_servidor = mysql.connector.connect(
            host='localhost',
            user='root',
            password='jcay2412'  # Tu contraseña real configurada
        )
        cursor_servidor = conexion_servidor.cursor()
        # Crea la base de datos saludMedica automáticamente si no existe en tu Workbench
        cursor_servidor.execute("CREATE DATABASE IF NOT EXISTS saludMedica")
        cursor_servidor.close()
        conexion_servidor.close()
        
        # Conexión oficial a la base de datos de trabajo
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='jcay2412',
            database='saludMedica'
        )
        cursor = conexion.cursor()
        
        # Creación automática de la tabla si no existe (Requerimiento 1 del PDF)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facturacion_citas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                paciente VARCHAR(256),
                especialidad VARCHAR(100),
                costo_base DECIMAL(10,2),
                descuento DECIMAL(10,2),
                igv DECIMAL(10,2),
                total DECIMAL(10,2)
            )
        """)
        conexion.commit()
        print("✅ Conexión establecida y tabla 'facturacion_citas' verificada.")
        
    except Error as e:
        print(f"❌ Error crítico al conectar con la Base de Datos: {e}")
        print("💡 Consejo: Asegúrate de tener tu servidor local MySQL encendido en el puerto 3306.")
        return

    # -------------------------------------------------------------------------
    # 2. TRANSFORMACIÓN Y LIMPIEZA DE DATOS (LÓGICA DE NEGOCIO)
    # -------------------------------------------------------------------------
    archivo_csv = 'citas_dia.csv'
    
    try:
        with open(archivo_csv, mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo)
            
            for fila in lector_csv:
                # Bloque try/except individual para omitir filas corruptas sin detener el script
                try:
                    paciente = fila.get('paciente', '').strip()
                    especialidad = fila.get('especialidad', '').strip()
                    
                    # Validación: Descartar si el campo especialidad está vacío (Requerimiento 2)
                    if not especialidad:
                        raise ValueError("Especialidad vacía.")

                    
                    # Intento de casteo numérico (Filtra textos erróneos como 'ErrorTipografico')
                    costo_base = float(fila.get('costo_base', 0))
                    
                    # Validación: Descartar si costo_base es menor o igual a 0 (Requerimiento 2)
                    if costo_base <= 0:
                        raise ValueError("Costo base inválido.")
                    
                    # Regla de descuento: 10% únicamente a "Pediatria"
                    if especialidad.lower() == "pediatria":
                        descuento = costo_base * 0.10
                    else:
                        descuento = 0.0
                    
                    # Cálculo de Impuestos: IGV (18%) sobre el costo neto tras el descuento
                    costo_con_descuento = costo_base - descuento
                    igv = costo_con_descuento * 0.18
                    
                    # Total a pagar sumando costo con descuento + IGV
                    total = costo_con_descuento + igv
                    
                    # -------------------------------------------------------------------------
                    # 3. CARGA (LOAD)
                    # -------------------------------------------------------------------------
                    query_insert = """
                        INSERT INTO facturacion_citas (paciente, especialidad, costo_base, descuento, igv, total)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query_insert, (paciente, especialidad, costo_base, descuento, igv, total))
                    registros_exitosos += 1
                    
                except (ValueError, TypeError):
                    # Cualquier falla de conversión o regla de negocio salta aquí y cuenta como descarte
                    registros_descartados += 1
                    
        # Confirmar permanentemente las inserciones exitosas en MySQL
        conexion.commit()
        
    except FileNotFoundError:
        print(f"❌ Error: El archivo '{archivo_csv}' no se encuentra en la carpeta raíz del proyecto.")
        return
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
            
    # Resumen impreso requerido por consola (Entregable 2 del PDF)
    print("\n" + "="*45)
    print(" 📊 RESUMEN DE LA EJECUCIÓN ETL")
    print("="*45)
    print(f" Total de registros procesados con éxito: {registros_exitosos}")
    print(f" Total de registros descartados por errores: {registros_descartados}")
    print("="*45)

if __name__ == '__main__':
    ejecutar_etl()
