#codigo de entrada

print ("##################################################")
print ("##################################################")
print ("Bienvenido al programa para el cálculo del tirante normal usando Manning")
print ("Tomado del escritorio de G_Guevara usando Python 3.9")

Q = float (input("introduzca la Caudal: ")) 
S = float (input("introduzca la pendiente: "))
N = float (input("introduzca la rugosidad: "))
B = float (input("introduzca el base: "))
Z = float (input("introduzca la talud: "))
#codigo de salida 

A=Q*N/(S**0.5)

Y=0.0
AA= float ((B+Z*Y)*Y)**(5/3)/((B+2*Y*(1+Z**2)**0.5)**(2/3))

while AA < A:
    Y = Y + 0.001
    AA= float ((B+Z*Y)*Y)**(5/3)/((B+2*Y*(1+Z**2)**0.5)**(2/3))

Tirante=round(Y,2)
Area=round((B+Z*Y)*Y,2)
Velocidad=round(Q/Area,2)

print ("##################################################")
print ("##################################################")

print("el tirante es: "+ str(Tirante)+ "  m")   
print("el Area hidráulica es: "+ str(Area)+ "  m2")   
print("la velocidad es: "+ str(Velocidad)+ "  m/s")           
   
   


