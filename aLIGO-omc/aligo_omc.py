# This code will define a standard aLIGO OMC, so I can separate my analysis into different notebooks
# without constantly copy the OMC FINESSE model defined first in aLIGO_OMC_Sim.ipynb

# Dependencies: FINESSE
import finesse
import cosmicexplorer.finesse.components as fc

class omc_builder:

    def __init__(self, inout = 51, highR = 7930, maxtem = None):
        self.inout = inout/1e6 #input-output coupler transmission in ppm
        self.highR = highR/1e6
        self.maxtem = maxtem

    def build(self): #Build da model
        omc = finesse.Model() #define model
        omc.modes(maxtem=self.maxtem)

        ###Vars###
        highref_T = self.highR #51ppm (measured transmission of high-refl, see LIGO-T1000276-v5)
        inout_T = self.inout #7930ppm (measured T of in/out couplers)
        aoi = 4 #angle of incidence in degrees
        roc = 2.575 #measured RoC of high-reflectors LIGO-T1000276-v5

        ###Input Beam###
        laser = omc.add(fc.Laser("Input", P=1)) #1W input laser power
        laser.tem(n=1,m=0,factor=1) #Forcing power into HOMs
        laser.tem(n=0,m=1,factor=1)
        laser.tem(n=1,m=1,factor=1)
        laser.tem(n=0,m=2,factor=1)
        laser.tem(n=2,m=0,factor=1)


        ###Mirrors###
        #Input/Output Couplers
        m1 = omc.add(fc.Beamsplitter("M1", R = 1-inout_T, T = inout_T, alpha=aoi)) #high reflectance, "thin" mirror
        m2 = omc.add(fc.Beamsplitter("M2", R = 1-inout_T, T = inout_T, alpha=aoi)) 

        #High-Reflectors 
        m3 = omc.add(fc.Beamsplitter("M3", R = 1-highref_T, T = highref_T,Rc=roc, alpha=aoi))
        m4 = omc.add(fc.Beamsplitter("M4", R = 1-highref_T, T = highref_T,Rc=roc, alpha=aoi))

        ###Spaces##
        s1 = omc.add(fc.Space("s1", portA=laser.p1, portB=m1.fr1,L=1)) #laser -> 1m -> m1 (length here makes no real difference)
        s2 = omc.add(fc.Space("s2", portA=m1.bk1, portB=m2.fr1,L=0.2815)) #m1 -> 0.2815m -> m2 #Lengths: LIGO-D1300507
        s3 = omc.add(fc.Space("s3", portA=m2.fr2, portB=m3.fr1,L=0.2842)) #m2 -> 0.2842m -> m3
        s4 = omc.add(fc.Space("s4", portA=m3.fr2, portB=m4.fr1,L=0.2815)) #m3 -> 0.2815m -> m4
        s5 = omc.add(fc.Space("s5", portA=m4.fr2, portB=m1.bk2,L=0.2842)) #m4 -> 0.2842m -> m1
                                                                
        ###Cavity###
        omc.add(fc.Cavity("OMC",m1.bk1.o,m3.fr1.i)) 

        return omc #return finesse Model object