import serial
import time
import csv
from datetime import datetime

puerto = 'COM3'  # Ajusta a tu puerto real
baudrate = 115200

# Obtener la hora de inicio para el nombre del archivo y el mensaje inicial
tiempo_inicio_dt = datetime.now()
tiempo_impresion = tiempo_inicio_dt.strftime('%H/%M/%S')
nombre_archivo = tiempo_inicio_dt.strftime('datos_IMU_%H-%M-%S.csv')

# Definir los nombres de las columnas (Tiempo + 12 variables)
columnas = [
    'Tiempo(s)',
    'IMU1_AccX', 'IMU1_AccY', 'IMU1_AccZ', 'IMU1_GyrX', 'IMU1_GyrY', 'IMU1_GyrZ',
    'IMU2_AccX', 'IMU2_AccY', 'IMU2_AccZ', 'IMU2_GyrX', 'IMU2_GyrY', 'IMU2_GyrZ'
]

try:
    ser = serial.Serial(puerto, baudrate, timeout=1)
    time.sleep(2)  # Espera a que la placa se reinicie y estabilice
    
    # Imprimir la hora de inicio (formato hora/minuto/segundo)
    print(f"--- Inicio de captura a las: {tiempo_impresion} ---")
    
    # PRIMERA IMPRESIÓN: Los nombres de las columnas en una sola línea
    print(", ".join(columnas))
    
    with open(nombre_archivo, mode='w', newline='') as archivo_csv:
        escritor = csv.writer(archivo_csv)
        
        # Escribir las cabeceras en el archivo CSV
        escritor.writerow(columnas)

        # Tomamos el tiempo exacto de referencia en segundos antes de entrar al bucle
        tiempo_inicio_segundos = time.time()

        while True:
            if ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8').rstrip()
                if not linea:
                    continue
                    
                valores_str = linea.split()
                
                # Verificamos que sigan llegando las 12 columnas de los IMU
                if len(valores_str) == 12:
                    try:
                        # 1. Calcular el tiempo transcurrido en segundos
                        tiempo_actual = time.time() - tiempo_inicio_segundos
                        
                        # 2. Convertir a flotantes los datos que llegaron
                        datos_imu = [float(v) for v in valores_str]
                        
                        # 3. Unir el tiempo (primera columna) con los datos de los sensores
                        fila_completa = [tiempo_actual] + datos_imu
                        
                        # 4. Imprimir en pantalla en una sola línea (tiempo con 3 decimales, IMUs con 4)
                        texto_pantalla = f"{tiempo_actual:.3f}, " + ", ".join([f"{v:.4f}" for v in datos_imu])
                        print(texto_pantalla)
                        
                        # 5. Exportar la fila directamente al CSV
                        escritor.writerow(fila_completa)
                        
                    except ValueError:
                        pass # Ignora basura serial para que el script no se caiga

except serial.SerialException as e:
    print(f"Error en el puerto: {e}")
except KeyboardInterrupt:
    print(f"\nCaptura detenida. Los datos se guardaron con éxito en: {nombre_archivo}")
    ser.close()