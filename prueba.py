import tkinter as tk
from tkinter import scrolledtext
import psutil
import platform
from datetime import datetime
import GPUtil

def bytes_a_gb(bytes):
    return round(bytes / (1024**3), 2)

def obtener_diagnostico():
    salida = ""

    # INFORMACIÓN DEL SISTEMA
    uname = platform.uname()
    salida += "=== INFORMACIÓN DEL SISTEMA ===\n"
    salida += f"Sistema Operativo : {uname.system}\n"
    salida += f"Nombre del PC      : {uname.node}\n"
    salida += f"Versión            : {uname.release}\n"
    salida += f"Arquitectura       : {uname.machine}\n"
    salida += f"Procesador         : {uname.processor}\n\n"

    # TIEMPO DE ACTIVIDAD
    salida += "=== TIEMPO DE ACTIVIDAD ===\n"
    bt = datetime.fromtimestamp(psutil.boot_time())
    salida += f"Último arranque: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}\n\n"

    # USO DE CPU
    salida += "=== USO DE CPU ===\n"
    cpu_usos = psutil.cpu_percent(percpu=True, interval=1)
    for i, percentage in enumerate(cpu_usos):
        salida += f"Núcleo {i}: {percentage}%\n"
    total_cpu = psutil.cpu_percent()
    salida += f"Uso total de CPU: {total_cpu}%\n\n"

    # USO DE MEMORIA RAM
    salida += "=== USO DE MEMORIA RAM ===\n"
    svmem = psutil.virtual_memory()
    salida += f"{'TOTAL (GB)':<15}{'USADA (GB)':<15}{'PORCENTAJE (%)':<15}\n"
    salida += f"{bytes_a_gb(svmem.total):<15}{bytes_a_gb(svmem.used):<15}{svmem.percent:<15}\n\n"

    # USO DE ALMACENAMIENTO
    salida += "=== USO DE ALMACENAMIENTO ===\n"
    salida += f"{'DISCO':<10}{'TOTAL (GB)':<15}{'USADO (GB)':<15}{'LIBRE (GB)':<15}{'USO (%)':<10}\n"
    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            salida += f"{particion.device:<10}{bytes_a_gb(uso.total):<15}{bytes_a_gb(uso.used):<15}{bytes_a_gb(uso.free):<15}{uso.percent:<10}\n"
        except PermissionError:
            continue
    salida += "\n"

    # INFORMACIÓN DE GPU
    salida += "=== INFORMACIÓN DE GPU ===\n"
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            salida += f"{gpu.name}: {gpu.load*100:.1f}% uso, {gpu.temperature}°C\n"
    except:
        salida += "No se pudo detectar GPU.\n"
    salida += "\n"

    # REVISIÓN DE PROCESOS
    salida += "=== REVISIÓN DE PROCESOS ===\n"
    procesos_sospechosos = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            nombre = proc.info['name']
            exe = proc.info['exe']
            if nombre and exe:
                if "temp" in exe.lower() or "appdata" in exe.lower():
                    procesos_sospechosos.append({
                        'nombre': nombre,
                        'ruta': exe
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if procesos_sospechosos:
        salida += f"⚠️ Se encontraron {len(procesos_sospechosos)} procesos sospechosos:\n"
        for proc in procesos_sospechosos[:5]:  # Mostrar solo los primeros 5
            salida += f"• {proc['nombre']} | Ruta: {proc['ruta']}\n"
        if len(procesos_sospechosos) > 5:
            salida += f"... y {len(procesos_sospechosos) - 5} procesos más\n"
    else:
        salida += "✅ No se detectaron procesos sospechosos.\n"

    salida += "\n"

    # ADVERTENCIAS
    salida += "=== ADVERTENCIAS ===\n"
    advertencias = []
    
    if total_cpu > 20:
        advertencias.append("⚠️ Alto uso de CPU")
    if svmem.percent > 50:
        advertencias.append("⚠️ Alto uso de memoria RAM")
    
    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            if uso.percent > 70:
                advertencias.append(f"⚠️ Poco espacio en disco en {particion.device}")
        except:
            continue
    
    try:
        for gpu in GPUtil.getGPUs():
            if gpu.load > 0.5:
                advertencias.append(f"⚠️ Alta carga de GPU: {gpu.name}")
            if gpu.temperature > 60:
                advertencias.append(f"⚠️ Alta temperatura de GPU: {gpu.name}")
    except:
        pass

    if advertencias:
        for adv in advertencias:
            salida += adv + "\n"
    else:
        salida += "✅ No se detectaron advertencias. Tu sistema está funcionando correctamente.\n"

    return salida

# INTERFAZ TKINTER
ventana = tk.Tk()
ventana.title("Diagnóstico del PC")
ventana.configure(bg="#7692ff")
ventana.geometry("900x750")
ventana.resizable(False, False)  # Bloquea el redimensionamiento horizontal y vertical
ventana.iconbitmap("mundo.ico")  # Agregamos el icono

text_area = scrolledtext.ScrolledText(ventana, width=100, height=40, bg="#7692ff", fg="white", cursor="heart")
text_area.pack(padx=10, pady=10)

def mostrar_diagnostico():
    diagnostico = obtener_diagnostico()
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, diagnostico)

boton = tk.Button(ventana, text="Ejecutar Diagnóstico", command=mostrar_diagnostico, cursor="hand2")
boton.pack(pady=10)

boton_salir = tk.Button(ventana, text="Salir", command=ventana.destroy, bg="red", fg="white", cursor="hand2")
boton_salir.pack(pady=5)

ventana.mainloop()
