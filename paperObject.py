#!/usr/bin/env python
# -*- coding: utf-8 -*-
from header import *
import numpy as np

#########################################################################
#numero de puntos a simular
n_0=15 
#tamaño particion a trabajar
NPart=100 
Part=[round(0.0 + i*(1./NPart),2) for i in range(NPart+1)]
#inicializo cada uno de los puntos(objetos)
Pts = [Lambda(x) for x in Part]
#simulacion inicial
Pts[0].simular()
Pts[-1].simular() 
#Realiza una primera ronda de predicciones
for i in range(1,NPart-1):
    Pts[i].predict(0.0,'Ant')
    Pts[i].predict(1.0,'Succ')
    
N=2
#Dado n0 puntos a simular
while N<= n_0:
    R=[] #Lista pesos 
    for y in range(NPart):
        if Pts[y].tipo=='p':
            x=Pts[y].valor        
            H_xa = Pts[y].ham['Ant']
            H_xs = Pts[y].ham['Succ']
            Ant  = Pts[y].Ant
            Succ = Pts[y].Succ
            #variacion o diferencia entre predicciones de puntos "vecinos"
            Diff=abs(H_xa-H_xs) 
            #asigno ponderación (peso) según distancia a ambos puntos vecinos
            w=(Succ-Ant)-abs((Succ-x)-(x-Ant)) 
            #Crear una lista del valor dado  a la "desconfianza" de cada punto
            R.append(desconfianza(w,Diff)) 
        else:
            R.append(-100)
    #Aquel punto con mayor valor en la lista es asignado como proximo a simular
    Q=Pts[np.argmax(R)] 
    Q.simular()
    #Se actualizan los vecinos de aquellos puntos predichos 
    for y in range(NPart):
        if Pts[y].tipo=='p':
            if Pts[y].ant!=Pts[y].ubicar(Pts)['Ant']:
                Pts[y].ant=Pts[y].ubicar(Pts)['Ant']
                Pts[y].predict(Pts[y].Ant,'Ant')
            if Pts[y].succ!=Pts[y].ubicar(Pts)['Succ']:
                Pts[y].succ=Pts[y].ubicar(Pts)['Succ']
                Pts[y].predict(Pts[y].Succ,'Succ')
    N+=1
    
#De aqui hay dos caminos, integrar a partir de estos puntos obtenidos, o bien, 
#Haciendo una combinacion convexa de las predicciones entre puntos vecinos 
#para aquellos no simulados. junto con una propagacion 
# del error respectivo a estos mismos

for y in range(NPart): 
    x=Pts[y].valor
    Y=Pts[y]
    if Y.tipo=='p':
        Ant  = Y.Ant
        Succ = Y.Succ

        w_a=(x-Succ)/(Ant-Succ) 
        w_s=(x-Ant)/(Succ-Ant)
        Y.ham= w_a*Y.ham['Ant'] + w_s*Y.ham['Succ']
        Y.err=np.sqrt( (w_a*Y.err['Ant'])**2 + (w_s*Y.err['Succ'])**2)
        
#Escribo un archivo que guarde la informacion final:
#valor del punto # predicho/simulado # valor energía #err asociado
with open('dHdlAdapt.dat','w') as F:
    F.write('#Pt\t'+'type\t'+'ham\t'+'errorEst\n')
    for x in Pts:
        F.write(str(x.valor)+'\t'+str(x.tipo)+'\t'+str(x.ham)+'\t'+str(x.err)+'\n')
F.close()

#integrar con trapezoide (o metodo de simpson) los puntos finales en el eje  x
#junto a sus valores respectivos en el eje y, graficar.
ys=[x.ham for x in Pts]
es=[x.err for x in Pts]
plotCurveErrors(Part,ys,es)
