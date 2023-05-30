from datetime import datetime, timedelta 

tiempo_expiracion = datetime.now() + timedelta(minutes=3)
print(tiempo_expiracion)

tiempo_actual = datetime.now()
print(tiempo_actual)

if tiempo_actual > tiempo_expiracion:
    print("Hola CTM")
elif tiempo_actual < tiempo_expiracion:
    print("hola vtalv")
