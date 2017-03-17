# -*- coding: utf-8 -*-
#!/usr/bin/env python
import numpy as np
import subprocess
import matplotlib.pyplot as plt

molec='ch4'
namebase='TI_'+molec+'_dummy'

class Lambda:
    #Defino la clase, junto con sus parametros clave
    def __init__(self,Pt, ant=0.0, succ=1.0, tipo='p', ham={},err={}):
        self.valor=Pt #valor del punto
        self.ant=ant  #punto anterior simulado 
        self.succ=succ #punto siguiente simulado
        self.tipo=tipo # 's' simulado, 'p' predicho(defecto)
        self.ham=ham # nivel de energía libre, dicc con estimacion si predicho
        self.err=err #error asociado al cálculo, error estimaciones si predicho
        
    #####Estas son para que funcione la función index en mi lista#######
    def __lt__(self,x):
        if type(x) == float:
            return self.valor < x
        return self.valor < x.valor
    def __gt__(self,x):
        if type(x) == float:
            return self.valor > x
        return self.valor > x.valor
        
    def __eq__(self,x):
        if type(x) == float:
            return self.valor == x
        return self.valor==self.x
    ###################################################################
    # entrega el valor de los puntos simulados más proximos en ambos sentidos{dicc}
        
    def ubicar(self, L):
        dict={}
        j=L.index(self.valor)
        i=j-1
        k=j+1
        while i>=0:
            L_i=L[i]
            if L_i.tipo=='s':
                dict['Ant']=L_i.valor
                break     
            i-=1
        while k<len(L):
            L_k=L[k]
            if L_k.tipo=='s':
                dict['Succ']=L_k.valor
                break
        return dict
        
    #Estas funciones reescriben los archivos a usar en simulacion
    #Joblist, input para ene_ana, script que ejecuta ene_ana, 
    #script que extrae output de ene_ana
    # 
    def writeJoblist(self):
        with open('TI_joblist.dat','w') as J:
            J.write('TITLE\n')
            J.write(' free energy profile for\n')
            J.write(' dissapearing a '+molec+' molecule in water\n')
            J.write('END\n')
            J.write('JOBSCRIPTS\n')
            J.write('job_id NSTLIM  RLAM    subdir   run_after\n')
            J.write('### lambda'+str(self.valor)+ '###\n')
            for i in range(1,7):
                jobnum = int(round(self.valor*10000)) +i
                if i ==1:
                    J.write(str(jobnum)+'\t10000\t0.0\tL_'+str(self.valor)+'\t-994\n')
                else:
                    J.write(str(jobnum)+'\t10000\t0.0\tL_'\
                                            +str(self.valor)+'\t'+str(jobnum-1)+'\n')
            J.write('END\n')
        J.close()
        
    def makeanalysis(self):
        namebase ='TI_ch4_dummy'        
        nsim = 6 
          
        with open('L_' +str(self.valor) +'/ene_ana.inp','w') as f:
            f.write('@fr_files\n')
            cnt =2
            while (cnt <= nsim):
                jobnum = int(round(self.valor*10000))+cnt
                f.write(namebase+'_'+str(jobnum) + '.trg.gz\n')
                cnt = cnt+1
            	
            f.write('@prop dvdl\n')
            f.write('@topo ../../topo/ch4_54a7.top\n')
            f.write('@library ../ene_ana.md++.lib\n')
            f.write('@time 0 0.2\n')
        f.close()
        
    def modRunanalysis(self):
        with open('runanalysis.csh','r') as M:
            data = M.readlines()
            data[4]='foreach x ('+ str(self.valor)+')\n'
        with open('runanalysis.csh','w') as M:
             for linea in data:
                 M.write(linea)
        M.close()
    
    def modExtractAve(self):
        with open('extract_ave.sh','r') as M:
            data = M.readlines()
            data[6]='for x in '+ str(self.valor)+'\n'
        with open('extract_ave.sh','w') as M:
            for linea in data:
                M.write(linea)
        M.close()
    
    def extraerHam(self):
        with open('dHdl.dat','r') as M:
            data = M.readlines()
            for linea in data:
                if linea.startswith(str(self.valor)):
                    L=linea.split()
                    break
            self.ham=L[1]
            self.err=L[2]
#Esta función modifica el input para mkscript pues el programa md modificado 
# no considera estos parametros automaticamente a la hora 
#de copiarlo en cada carpeta
                    
    def MODimd(self):
        namebase ='TI_ch4_dummy'
        cnt =1
        nsim = 6 
        while (cnt <= nsim):
             jobnum = int(round(self.valor*10000))+cnt
             with open('L_' +str(self.valor) +'/'\
                                       +namebase+'_'+str(jobnum)+'.imd','r') as f:
                 data=f.readlines()
                 for linea in data:
                     if linea.startswith('COVALENTFORM'):
                         pos=data.index(linea)
                         data.insert(pos+3,'#\tPNTBBH\tPNTBAH\tPNTBDN\tPOWLAMB\n')
                         data.insert(pos+4,'\t2\t0\t0\t12\n')
                     if linea.startswith('WRITETRAJ'):
                         pos=data.index(linea)
                         data[pos+2]='\t250\t0\t0\t0\t100\t100\t0\n'
             with open('L_' +str(self.valor) +'/'\
                                       +namebase+'_'+str(jobnum)+'.imd','w') as f:
                 for linea in data:
                     f.write(linea)
             f.close()
             cnt = cnt+1
##########################################################################
#Función que ejecuta todas las instrucciones para simular un punto, junto con
#guardar su información relevante y cambiar su atributo a simulado
             
    def simular(self):
        
        self.writeJoblist()
        ###Aqui ejecuto las instrucciones de simulacion tipicas
        subprocess.call('mk_script @f TI_mk_script.arg', shell=True)
        self.MODimd()
        jobnum = int(round(self.valor*10000))+1
        subprocess.call('./L_'+str(self.valor)+'/'+namebase+'_'\
                                        +str(jobnum)+'.run',shell=True)
        
        self.makeanalysis()
        
        self.modRunanalysis()
        subprocess.call('./runanalysis.csh',shell=True)
        
        self.modExtractAve()
        subprocess.call('./extract_ave.sh',shell=True)
        
        
        self.extraerHam()
        self.tipo='s'

#funcion que extrae informacion sobre este punto en la configuración de algun 
#punto simulado, indicando si este es mayor o menor que el
        
    def predict(self,x,pos): 
        pred= 'pred'+str(self.valor)
        reweight='reweight'+str(self.valor)
        with open('eneanapred.inp','w') as M:
            M.write('@fr_files \n')
            nsim=6
            cnt =2
            direc='./L_'+str(x)+'/'
            while (cnt <= nsim):
                jobnum = int(round(x*10000))+cnt
                M.write(direc+namebase+'_'+str(jobnum) + '.trg.gz\n')
                cnt = cnt+1
            M.write('@en_files \n')
            cnt =2
            while (cnt <= nsim):
                jobnum = int(round(x*10000))+cnt
                M.write(direc+namebase+'_'+str(jobnum) + '.tre.gz\n')
                cnt = cnt+1
            M.write('@prop '+pred+'\t'+reweight+'\t'+'\n')
            M.write('@topo ../topo/'+molec+'_54a7.top \n')
            M.write('@library ./ene_ana.md++.lib \n')
            M.write('@time 0 0.2 \n')
        M.close()
        subprocess.call('ene_ana @f eneanapred.inp > eneanapred.out',shell=True)
        with open('eneanapred.out','r') as M:
            data=M.readlines()
            param=pred
            for linea in data:
                if linea.startswith(param):
                    mito_pred=linea.split()[1]
                    mito_pred_err=linea.split()[3]
                    break
            param=reweight
            for linea in data:
                if linea.startswith(param):
                    mito_reweight=linea.split()[1]
                    mito_reweight_err=linea.split()[3]
                    break
        M.close()
        self.ham[pos]=mito_pred/mito_reweight
        self.err[pos]=np.abs(self.ham[pos])*np.sqrt((mito_pred_err/mito_pred)**2 +\
                                            (mito_reweight_err/mito_reweight)**2)
#funcion que mide que tanta seguridad se tiene sobre la informacion de cada punto
def desconfianza(w,diff,err=0):
    a=0
    b=0
    c=0
    m=0
    tol=1.0
    s1=diff *w *|tol -err|^m
    s2=w*diff*{err**m}
    s3=a*w + b*diff +c*err
    return s2
def plotCurveErrors(xs, ys, es):
    quad=np.trapz(ys,xs)
    fig = plt.figure()
    fig.hold(True)
    ax11 = fig.add_subplot(111)
    ax11.errorbar(xs, ys, yerr=es, color="k", \
                  ecolor="r", mfc="k", marker="o", ms=4.0, linestyle='--')
    ax11.set_xlabel(r'${\lambda}$')
    ax11.set_ylabel(r'<dV/d${\lambda}$>')
    plt.text(60, .025, r'$\Delta F=$ '+'$'+str(quad)+'$')

    return fig
def MODene_anaLIB(NPart):
    with open('ene_ana.md++.lib','r') as LIB:
        data=LIB.readlines()
        for linea in data:
            if linea.startswith('VARIABLES'):
                pos=data.index(linea)
                for i in range(NPart+1):
                    pred='pred'+str(round(0.0 + i*(1./NPart),2))+\
                         '=FREEPRECALCLAM['+str(i+1)+'][1]\n'
                    reweight='reweight'+str(round(0.0 + i*(1./NPart),2))+\
                    '=exp(-(PRECALCLAM['+str(i+1)+'][1]-ENER[3])/(BOLTZ*TEMP))\n'
                    data.insert(pos+2*i+1,pred)
                    data.insert(pos+2*i+2,reweight)
                break
    with open('ene_ana.md++.lib','w') as LIB:
        for linea in data:
            LIB.write(linea)
    LIB.close()
    
#