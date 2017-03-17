#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
NPart=100
MODene_anaLIB(NPart)