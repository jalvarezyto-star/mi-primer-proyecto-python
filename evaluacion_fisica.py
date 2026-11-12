# Solicitar datos al usuario y convertir tipos
nombre = input("Ingresa tu nombre: ")
edad = int(input("Ingresa tu edad: "))
peso = float(input("Ingresa tu peso en kg: "))
horas_ejercicio = float(input("Ingresa tus horas de ejercicio a la semana: "))

# Calcular calorías quemadas estimadas
calorias_quemadas = horas_ejercicio * 350

# Evaluar categoría por edad
if edad < 18:
    categoria = "Categoría: Juvenil"
else:
    categoria = "Categoría: Adulto"

# Evaluar estado físico por sedentarismo
if horas_ejercicio >= 3:
    estado = "Estado: Físicamente Activo"
else:
    estado = "Estado: Requiere mayor actividad física"

# Imprimir resumen con f-strings
print("\n--- Resumen de Evaluación Física ---")
print(f"Nombre: {nombre}")
print(f"Peso registrado: {peso} kg")
print(f"Calorías quemadas estimadas a la semana: {calorias_quemadas} kcal")
print(categoria)
print(estado)
