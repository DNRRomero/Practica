adaptación del paper usando varianza de la estimación
	Se inicia con el método original del paper, el cual es básicamente ir generando una predicción de los niveles 
	de energía de todos los puntos a partir de una configuración fija, dado que inicialmente se realiza una simulación
	de los estados inicial y final, se realiza una "predicción" de los niveles intermedios a través del método mencionado
	usando como enfoque a los "vecinos simulados" de cada uno de estos puntos luego, 
	dado una diferencia de las estimaciones, la estimación del error asociado a cada punto (el cual depende de F'')
	y de una ponderación relacionada con la distancia que se tiene de los "puntos vecinos" a partir de los cuales
	realicé la predicción, se construye una función que entrega como máximo el punto considerado
	de "mayor desconfianza", para luego simular dicho punto.
	Se itera sobre este método hasta cumplir con la cantidad de puntos planteada y, finalmente, se considera
	una combinación convexa de las ultimas predicciones de cada punto no simulado.
	
	n0= puntos a simular
	NPart= tamaño particion
	Construir Lista Pts con objeto Pt por cada valor equiespaciado segun NPart
	Simulo el primer(0.0) y el último (1.0) puntos
	for i in particion, distinto a cero y uno:
		predecir hamiltoniano a partir de 0.0 y 1.0 ("antecesor" y "sucesor" siendo estos sus vecinos simulados)
	N=2
	While N<= n0 (puntos a simular)
	
		for in Pts predichos
			Diff = diferencia entre predicciones.
			Peso = ponderación según que tan alejado está del antecesor y sucesor
			R= f(Diff, Peso, var) /construyo una función que use como criterio
									la varianza de la estimación y los coef anteriores
		Q= argmax( R for R de punto predicho)
		Simulo Q.
		Actualizo los vecinos de cada pt predicho
	Una vez simulados todos mis puntos, tomo una combinación convexa de las predicciones de c/vecinos
	Integro mediante trapezoide.
	
Candidatos a f: 
        1-Diff *Peso *|tol -var|^m  //  tol= tolerancia que quiero darle al error, y estudiar m que apañe
				2-
				3-
