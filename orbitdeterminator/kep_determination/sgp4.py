'''
The code takes a TLE and computes state vectors for next 8 hrs at every second.
'''

import numpy as np
import math

pi = np.pi
meu = 398600.4418
two_pi = 2*pi;
min_per_day = 1440

class SGP4(object):

    def propagate(self, line1, line2):
        '''
        Computes state vectors at every second for 8 hours and stores them into
        a vector and returns the final vector.

        Args:
            self: class variables
            line1: line 1 in TLE
            line2: line 2 in TLE

        Returns:
            final: vector containing all state vectors for 8 hours
        '''

        self.xmo = float(''.join(line2[43:51])) * (pi/180)
        self.xnodeo = float(''.join(line2[17:25])) * (pi/180)
        self.omegao = float(''.join(line2[34:42])) * (pi/180)
        self.xincl = float(''.join(line2[8:16])) * (pi/180)
        self.eo = float('0.'+str(''.join(line2[26:33])))
        self.xno = float(''.join(line2[52:63]))*two_pi/min_per_day
        self.bstar = int(''.join(line1[53:59]))*(1e-5)*(10**int(''.join(line1[59:61])))

        final = np.zeros((28800,6))
        i = 0
        upto = 28800                # 28800 secs in 8 hours (in seconds)
        while(i < upto):
            tsince = i
            pos, vel = self.propagation_model(tsince)
            data = [pos[0], pos[1], pos[2], vel[0], vel[1], vel[2]]
            data = [float("{0:.5f}".format(i)) for i in data]
            print(str(tsince) + " - " + str(data))
            final[i,:] = data
            i = i + 1

        return final

    def propagation_model(self, tsince):
        '''
        Computes state vectors at a given time epoch.

        Args:
            self: class variables
            tsince: time epoch

        Returns:
            pos: position vector
            vel: velocity vector
        '''
        ae = 1
        tothrd = 2.0/3.0
        XJ3 = -2.53881e-6
        e6a = 1.0E-6
        xkmper = 6378.135
        ge = 398600.8           # Earth gravitational constant
        CK2 = 1.0826158e-3/2.0
        CK4 = -3.0*-1.65597e-6/8.0

        # Constants
        s = ae + 78 / xkmper
        qo = ae + 120 / xkmper
        xke = math.sqrt((3600 * ge)/(xkmper**3))
        qoms2t = ((qo-s)**2)**2
        temp2 = xke/self.xno
        a1 = temp2**tothrd
        cosio = math.cos(self.xincl)
        theta2 = cosio**2
        x3thm1 = 3*theta2-1
        eosq = self.eo**2
        betao2 = 1-eosq
        betao = math.sqrt(betao2)
        del1 = (1.5*CK2*x3thm1)/((a1**2)*betao*betao2)
        ao = a1*(1-del1*((1.0/3.0)+del1*(1+(134.0/81.0)*del1)))
        delo = 1.5*CK2*x3thm1/((ao**2)*betao*betao2)
        xnodp = (self.xno)/(1+delo)
        aodp = ao/(1-delo)

        # Initialization
        isimp = 0
        if((aodp*(1-self.eo)/ae) < (220.0/xkmper+ae)):
            isimp = 1

        s4 = s
        qoms24 = qoms2t
        perigee = (aodp*(1-self.eo)-ae)*xkmper
        if(perigee < 156):
            s4 = perigee - 78
            if(perigee <= 98):
                s4 = 20
            qoms24 = ((120-s4)*ae/xkmper)**4
            s4 = s4/xkmper+ae

        pinvsq = 1/((aodp**2)*(betao2**2))
        tsi = 1/(aodp-s4)
        eta = aodp*(self.eo)*tsi
        etasq = eta**2
        eeta = (self.eo)*eta
        psisq = abs(1-etasq)
        coef = qoms24*(tsi**4)
        coef1 = coef/(psisq**3.5)
        c2 = coef1*xnodp*(aodp*(1+1.5*etasq+eeta*(4+etasq))+0.75*CK2*tsi/psisq*x3thm1*(8+3*etasq*(8+etasq)))
        c1 = self.bstar*c2
        sinio = math.sin(self.xincl)
        a3ovk2 = -XJ3/CK2*(ae**3)
        c3 = coef*tsi*a3ovk2*xnodp*ae*sinio/self.eo
        x1mth2 = 1-theta2
        c4 = 2*xnodp*coef1*aodp*betao2*(eta*(2.0+0.5*etasq)+(self.eo)*(0.5+2*etasq)-2*CK2*tsi/(aodp*psisq)*(-3*x3thm1*(1-2*eeta+etasq*(1.5-0.5*eeta))+0.75*x1mth2*(2*etasq-eeta*(1+etasq))*math.cos(2*self.omegao)))
        c5 = 2*coef1*aodp*betao2*(1+2.75*(etasq+eeta)+eeta*etasq)
        theta4 = theta2**2
        temp1 = 3*CK2*pinvsq*xnodp
        temp2 = temp1*CK2*pinvsq
        temp3 = 1.25*CK4*(pinvsq**2)*xnodp
        xmdot = xnodp+0.5*temp1*betao*x3thm1+0.0625*temp2*betao*(13-78*theta2+137*theta4)
        x1m5th = 1-5*theta2
        omgdot = -0.5*temp1*x1m5th+0.0625*temp2*(7-114*theta2+395*theta4)+temp3*(3-36*theta2+49*theta4)
        xhdot1 = -temp1*cosio
        xnodot = xhdot1+(0.5*temp2*(4-19*theta2)+2*temp3*(3-7*theta2))*cosio
        omgcof = self.bstar*c3*math.cos(self.omegao)
        xmcof = -(2/3)*coef*(self.bstar)*ae/eeta
        xnodcf = 3.5*betao2*xhdot1*c1
        t2cof = 1.5*c1
        xlcof = 0.125*a3ovk2*sinio*(3+5*cosio)/(1+cosio)
        aycof = 0.25*a3ovk2*sinio
        delmo = (1+eta*math.cos(self.xmo))**3
        sinmo = math.sin(self.xmo)
        x7thm1 = 7*theta2-1
        if(isimp == 0):
            c1sq = c1**2
            d2 = 4*aodp*tsi*c1sq
            temp = d2*tsi*c1/3
            d3 = (17*aodp+s4)*temp
            d4 = 0.5*temp*aodp*tsi*(221*aodp+31*4)*c1
            t3cof = d2+2*c1sq
            t4cof = 0.25*(3*d3+c1*(12*d2+10*c1sq))
            t5cof = 0.2*(3*d4+12*c1*d3+6*(d2**2)+15*c1sq*(2*d2+c1sq))

        xmdf = self.xmo+xmdot*tsince
        omgadf = self.omegao+omgdot*tsince
        xnoddf = self.xnodeo+xnodot*tsince
        omega = omgadf
        xmp = xmdf
        tsq = tsince**2
        xnode = xnoddf+xnodcf*tsq
        tempa = 1 - c1*tsince
        tempe = self.bstar*c4*tsince
        templ = t2cof*tsq
        if(isimp == 0):
            delomg = omgcof*tsince
            delm = xmcof*(((1+eta*math.cos(xmdf))**3)-delmo)
            temp = delomg+delm
            xmp = xmdf+temp
            omega = omgadf-temp
            tcube = tsq*tsince
            tfour = tsince*tcube
            tempa = tempa-d2*tsq-d3*tcube-d4*tfour
            tempe = tempe+self.bstar*c5*(math.sin(xmp)-sinmo)
            templ = templ+t3cof*tcube+tfour*(t4cof+tsince*t5cof)

        a = aodp*(tempa**2)
        e = self.eo-tempe
        xl = xmp+omega+xnode+xnodp*templ
        beta = math.sqrt(1-e**2)
        xn = xke/(a**1.5)

        axn = e*math.cos(omega)
        temp = 1/(a*(beta**2))
        xll = temp*xlcof*axn
        aynl = temp*aycof
        xlt = xl+xll
        ayn = e*math.sin(omega)+aynl
        diff = xlt - xnode
        capu = diff - math.floor(diff/two_pi) * two_pi
        if(capu < 0):
            capu = capu + two_pi
        temp2 = capu

        i = 1
        while(1):
            sinepw = math.sin(temp2)
            cosepw = math.cos(temp2)
            temp3 = axn*sinepw
            temp4 = ayn*cosepw
            temp5 = axn*cosepw
            temp6 = ayn*sinepw
            epw = (capu-temp4+temp3-temp2)/(1-temp5-temp6)+temp2
            temp7 = temp2
            temp2 = epw
            i = i + 1
            if((i>10) | (abs(epw-temp7)<=e6a)):
                break

        ecose = temp5+temp6
        esine = temp3-temp4
        elsq = axn**2 + ayn**2
        temp = 1-elsq
        pl = a*temp
        r = a*(1-ecose)
        temp1 = 1/r
        rdot = xke*math.sqrt(a)*esine*temp1
        rfdot = xke*math.sqrt(pl)*temp1
        temp2 = a*temp1
        betal = math.sqrt(temp)
        temp3 = 1/(1+betal)
        cosu = temp2*(cosepw-axn+ayn*esine*temp3)
        sinu = temp2*(sinepw-ayn-axn*esine*temp3)
        u = math.atan2(sinu, cosu)
        if(u < 0):
            u = u + two_pi

        sin2u = 2*sinu*cosu
        cos2u = 2*(cosu**2)-1
        temp = 1/pl
        temp1 = CK2*temp
        temp2 = temp1*temp

        rk = r*(1-1.5*temp2*betal*x3thm1)+0.5*temp1*x1mth2*cos2u
        uk = u-0.25*temp2*x7thm1*sin2u
        xnodek = xnode+1.5*temp2*cosio*sin2u
        xinck = self.xincl+1.5*temp2*cosio*sinio*cos2u
        rdotk = rdot-xn*temp1*x1mth2*sin2u
        rfdotk = rfdot+xn*temp1*(x1mth2*cos2u+1.5*x3thm1)

        MV = [-math.sin(xnodek)*math.cos(xinck), math.cos(xnodek)*math.cos(xinck), math.sin(xinck)]
        NV = [math.cos(xnodek), math.sin(xnodek), 0]

        UV = [0, 0, 0]
        VV = [0, 0, 0]
        for i in range(3):
            UV[i] = MV[i]*math.sin(uk) + NV[i]*math.cos(uk)
            VV[i] = MV[i]*math.cos(uk) - NV[i]*math.sin(uk)

        pos = [0, 0, 0]
        vel = [0, 0, 0]
        for i in range(3):
            pos[i] = rk*UV[i]*xkmper
            vel[i] = (rdotk*UV[i] + rfdotk*VV[i])*xkmper/60

        return pos, vel

if __name__ == "__main__":
    line1 = "1 88888U          80275.98708465  .00073094  13844-3  66816-4 0     8"
    line2 = "2 88888  72.8435 115.9689 0086731  52.6988 110.5714 16.05824518   105"

    obj = SGP4()
    state_vec = obj.propagate(line1, line2)
    # print(state_vec)
    del(obj)