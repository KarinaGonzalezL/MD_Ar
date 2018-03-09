#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 14:17:48 2018

@author: karinagl
"""

import random
import math
import copy
import numpy as np
import os
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3           
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D  
import sys         

        
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#---------------Useful classes------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Atom(object):
    def __init__(self):
        self.x=0
        self.y=0
        self.z=0
        self.vx=0
        self.vy=0
        self.vz=0
        self.fx=0
        self.fy=0
        self.fz=0
        self.potential = 0
        self.kinetic=0

    def setNonSpecificParameters(self,mass,epsilon, sigma):
        self.mass=float(mass)
        self.epsilon=float(epsilon)
        self.sigma= float(sigma)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++      
class writeFile:
    def __init__(self):
        try:
            os.remove("vac.csv")
        except OSError:
            pass
        try:
            os.remove("lj.xyz")
        except OSError:
            pass
        
        with open("lj.xyz", "a") as output:
            output.write('TITLE     my_system t= %.5f\n' % (step * dt))
            output.write("864\n") #Number of atoms
    def writeData(self,filename,data):
        with open(filename, "a") as output:
            for point in data:
                output.write("%s\n" % point)
    def writeXYZ(self,atoms):
        with open("lj.xyz", "a") as output:
            for atom in atoms:
                output.write("Ar %s %s %s\n" %(atom.x,atom.y,atom.z))
                
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++                     
class Simulation:
    
    kb = 1.380e-23                  # Boltzmann (J/K)
    Nav = 6.022e23                  # Molecules/mol
    mass = (39.95/Nav)*(10**-3)     # mass of a single atom , Kg
    epsilon = kb*120                # depth of potential well, J
    sigma =3.4e-10                 # sigma in Lennard-Jones Potential, meters
    rcut = 2.25*sigma               # Cutoff radius, meters
    rcutsq = rcut**2                # Square of the cutoff radius.
    temp = 90                       # Temperature, K
    lbox = 10.229*sigma             # 10.229length of the box. (meters)
    currentTemp = 0                 # System temperature
    dt = 1.0e-3                     # timestep
    
    NumberOfAtoms = 864
    temperatures = []
    atoms= []
    potentials=[]
    #kinetics = []
    
    print("EmpiezalaclaseSimulacion")  
    def __init__(self):
        """Creates a simulation with NumberOfAtoms"""
        print("initializing system...")
        for i in range(0,self.NumberOfAtoms):
            self.atoms.append(Atom())
        self.assignPositions()
        self.correctMomentum()
        print("Done")
        print("Simulation is runnning")
    
#    def assignPositions(self):
#        """Places each atom in arbitrary positions in the box."""
#        particle=0
#        R= np.zeros([self.NumberOfAtoms,3]) 
#        fig = plt.figure()
#        ax = p3.Axes3D(fig)
#        for atom in range(self.NumberOfAtoms):
#                
#                self.atoms[atom].x = 2*random.random()-1
#                self.atoms[atom].y = 2*random.random()-1
#                self.atoms[atom].z = 2*random.random()-1
#                particle +=1
#                #print(self.atoms[atom].x,self.atoms[atom].y,self.atoms[atom].z)
#                R = np.array([self.atoms[atom].x,self.atoms[atom].y, self.atoms[atom].z])
#
#
#               
#                ax.scatter(R[0],R[1],R[2], "-")
#                ax.set_xlabel('X')
#                ax.set_ylabel('Y')
#                ax.set_zlabel('Z')
#        plt.show()
        
    def assignPositions(self):
        """Places each atom in arbitrary positions in the box."""
#        print("nuemerodeatomos",self.NumberOfAtoms)
#        n = int(math.ceil(self.NumberOfAtoms**(1.0/3.0))) # Number of atoms in a direction
#        print("n",n)
#        print("mathceil",self.NumberOfAtoms**(1.0/3.0))
#        particle = 0 
#        for x in range(0, n):
#            for y in range(0, n):
#                for z in range(0, n):
#                    if (particle < self.NumberOfAtoms):
#                        self.atoms[particle].x = x * self.sigma
#                        self.atoms[particle].y = y * self.sigma             
#                        self.atoms[particle].z = z * self.sigma
#                        particle += 1 
        
        
               
    def applyBoltzmannDist(self):
        """Applies Boltzmann dist to velocities"""
        normDist = []
        scaling_factor = math.sqrt(self.kb*self.temp/self.mass)

        #Normal distribution
        for i in range(0,self.NumberOfAtoms):
            normDist.append(random.gauss(0,1))
            
        #Apply scaling factor to dist
        for number in range(0,3*self.NumberOfAtoms):
            normDist[number]=normDist[number]*scaling_factor
            
        #Distribute velocities
        for atom in range(0,self.NumberOfAtoms):
            self.atoms[atom].x = normDist[atom*3]
            self.atoms[atom].x = normDist[atom*3+1]
            self.atoms[atom].x = normDist[atom*3+2]
        
    def correctMomentum(self):
        sumvx=0
        sumvy=0
        sumvz=0
        
        for atom in range(0, self.NumberOfAtoms):
            sumvx += self.atoms[atom].vx
            sumvy += self.atoms[atom].vy
            sumvz += self.atoms[atom].vz

        # Velocity standard deviation        
        for atom in range(0,self.NumberOfAtoms):
            self.atoms[atom].vx -= sumvx/self.NumberOfAtoms
            self.atoms[atom].vy -= sumvy/self.NumberOfAtoms
            self.atoms[atom].vz -= sumvz/self.NumberOfAtoms

        
    def runSimulation(self, step, numSteps):
        self.updateForces()
        self.verletIntegration()
        self.updateTemperature()
        self.updatePotentials()
        self.resetForces()
        if (step+1) % 10 == 0:
            print("----Completed step" + str(step+1)+"/"+str(numSteps)+ "------")
        #After 100steps, scale the temp by a factor Tdesired(T(t))
        if step > 20 and step <120:
            self.scaleTemperature()
            
    def updateForces(self):
        """Calculate net potential applyng the cutoff radius"""
        for atom1 in range(0,self.NumberOfAtoms-1):
            for atom2 in range(atom1+1,self.NumberOfAtoms):
                self.lj_force(atom1,atom2)

                 
        for atom in range(0,self.NumberOfAtoms):
            self.atoms[atom].fx *= 48*self.epsilon
            self.atoms[atom].fy *= 48*self.epsilon
            self.atoms[atom].fz *= 48*self.epsilon
            self.atoms[atom].potential *= 4*self.epsilon
#            self.atoms[atom].kinetic *= 0.5/self.m
            
    def lj_force(self, atom1,atom2):
        """Calculates the force between 2 atoms using LJpot"""
        #distance btwn x_{i} and x_{j}, thus reducing 27variables to 9
        dx=self.atoms[atom1].x - self.atoms[atom2].x 
        dy=self.atoms[atom1].y - self.atoms[atom2].y
        dz=self.atoms[atom1].z - self.atoms[atom2].z

        # minimum image convention
        dx -= self.lbox*round(dx/self.lbox)
        dy -= self.lbox*round(dy/self.lbox)
        dz -= self.lbox*round(dz/self.lbox)

        
    #length=r
        r2 = dx*dx+dy*dy+dz*dz
        
    #Since is a central force prob F=-grad(pot)= pot (qi/r2)
        if r2 < self.rcutsq:
            fr2 = (self.sigma**2)/r2
            fr6 = fr2**3
            ljForce= fr6*(fr6-0.5)/r2
            
            Pot= fr6*(fr6-1)
            
      #Force_atom1=-Force_atom2  
      #update forces
            self.atoms[atom1].fx += ljForce*dx
            self.atoms[atom2].fx -= ljForce*dx
            self.atoms[atom1].fy += ljForce*dy
            self.atoms[atom2].fy -= ljForce*dy
            self.atoms[atom1].fz += ljForce*dz
            self.atoms[atom2].fz -= ljForce*dz   
            
        #update potentials
            self.atoms[atom1].potential += Pot
            self.atoms[atom2].potential += Pot
        
    def verletIntegration(self):
        """Moves the system through a given time step, according to the energies"""
        for atom in range(0, self.NumberOfAtoms):
            
            # Update velocities
            #v_new = v + (lj_force(R) + lj_force(R_new))/2 * dt
            self.atoms[atom].vx += (self.atoms[atom].fx/self.mass)*self.dt
            self.atoms[atom].vy += (self.atoms[atom].fy/self.mass)*self.dt
            self.atoms[atom].vz += (self.atoms[atom].fz/self.mass)*self.dt
            #print("lasvelocidades",self.atoms[atom].vx,self.atoms[atom].vy,self.atoms[atom].vz)

            # Update positions
            #Instead of updating R, I update x,y,z separately
            #R_new = R + v * dt + lj_force(R) * dt ** 2 / 2 
            newX = self.atoms[atom].x + self.atoms[atom].vx*self.dt
            newY = self.atoms[atom].y + self.atoms[atom].vy*self.dt
            newZ = self.atoms[atom].z + self.atoms[atom].vz*self.dt
            
            # Update current positions (applying PBC)
            #I guess we have to use something more fancy
            if newX < 0:
                self.atoms[atom].x = newX + self.lbox
            elif newX > self.lbox:
                self.atoms[atom].x = newX - self.lbox
            else:
                self.atoms[atom].x = newX
            
            if newY < 0:
                self.atoms[atom].y = newY + self.lbox
            elif newY > self.lbox:
                self.atoms[atom].y = newY - self.lbox
            else:
                self.atoms[atom].y = newY
                
            if newZ < 0:
                self.atoms[atom].z = newZ + self.lbox
            elif newZ > self.lbox:
                self.atoms[atom].z = newZ - self.lbox
            else:
                self.atoms[atom].z = newZ   
                
        
    def resetForces(self):
        """set all forces to zero"""
        for atom in range(0,self.NumberOfAtoms):
            self.atoms[atom].fx=0
            self.atoms[atom].fy=0
            self.atoms[atom].fz=0
            self.atoms[atom].Pot=0
            
    def updateTemperature(self):
        """Calculates the current system temp"""
        sumv2=0
        for atom in self.atoms:
            sumv2 += atom.vz**2 + atom.vy**2 + atom.vz**2
        self.currentTemp = (self.mass/(3*self.NumberOfAtoms*self.kb))*sumv2
        self.temperatures.append(self.currentTemp)
            
            
    def updatePotentials(self):
        epot=0
        for atom in (self.atoms):
            epot += atom.potential
        self.potentials.append(epot)


#A deep copy constructs a new compound object and then, recursively
#inserts copies into it of the objects found in the original.
    def getAtoms(self):
        return copy.deepcopy(self.atoms)
    
    def scaleTemperature(self):
        """Scales the temp according to the desired temp"""
        if self.currentTemp > 100.0 or self.currentTemp < 80.0:
            print("Rescaling velocities...")
            for atom in range(0,self.NumberOfAtoms):
                self.atoms[atom].vx *= math.sqrt(self.temp/self.currentTemp)
                self.atoms[atom].vy *= math.sqrt(self.temp/self.currentTemp)
                self.atoms[atom].vz *= math.sqrt(self.temp/self.currentTemp)
                

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Analysis:
    
    kb = 1.380e-23                  # Boltzmann (J/K)
    sigma = 3.4e-10                 # sigma in Lennard-Jones Potential, meters
    dr = sigma/10                   # (1/100)*sigma
    dt = 1.0e-3                     # timestep
    V = (10.229*sigma)**3           #Volume of the box
    lbox = 10.229*sigma
    velacfinit= 0                   #Velocity autocorrelation funct a timestep
    velacf = 0                      #Velocity autocorrelation function at a time step
    
    NumberOfAtoms = 864
    
    currentAtoms = []
    nr = [] #number of particles in radius r
    originalAtoms = []
    velUpdList = []
    radUpdList = []
    timeUpdList = []
    
    print("Empiezaelanalisis")
    def __init__(self,atoms):
        """Initalize the analysis with the atoms int their initial state"""
        self.originalAtoms = atoms
    
    def updateAtoms(self,atoms):
        """update state of Atmos"""
        self.currentAtoms = atoms
        
    def pairDistFunc(self):
        atom_counts = [0]*50
        cur_r = 0
        
        print("Generating rdf")
        
        
        for atom1 in range(0,self.NumberOfAtoms-1):
            for atom2 in range(1,self.NumberOfAtoms):
                
                dx = self.currentAtoms[atom1].x - self.currentAtoms[atom2].x
                dy = self.currentAtoms[atom1].y - self.currentAtoms[atom2].y
                dz = self.currentAtoms[atom1].z - self.currentAtoms[atom2].z
                 
                dx -= self.lbox*round(dx/self.lbox)
                dy -= self.lbox*round(dy/self.lbox)
                dz -= self.lbox*round(dz/self.lbox)
                        
        #length=r
                r2 = dx*dx+dy*dy+dz*dz
                r = math.sqrt(r2)
                
                for radius in range (0,50):
                    if (r < ((radius+1)*self.dr)) and (r > radius*self.dr):
                        atom_counts[radius] +=1
        #assert len(atom1) == len(atom2)
        
        for radius in range(1,50):
            atom_counts[radius] *= (self.V/self.NumberOfAtoms**2)/(4*math.pi*((radius*self.dr)**2)*self.dr)
        print("done con los radios")
        return(atom_counts)
        
    def velAutocorrelation(self,step):
        vx=0
        vy=0
        vz=0
            
        if step ==0:
            for atom in range(0,self.NumberOfAtoms):
    
                vx += self.originalAtoms[atom].vx*self.currentAtoms[atom].vx
                vy += self.originalAtoms[atom].vy*self.currentAtoms[atom].vy
                vz += self.originalAtoms[atom].vz*self.currentAtoms[atom].vz    
                
            self.velacfinit += vx+vy+vz
            #print("velacfinit",self.velacfinit)
            self.velacfinit /= self.NumberOfAtoms
            self.velUpdList.append(self.velacfinit)
        else:
            for atom in range(0,self.NumberOfAtoms):
                #print("original vx",self.originalAtoms[atom].vx,"original vy",self.originalAtoms[atom].vy )
                vx += self.originalAtoms[atom].vx * self.currentAtoms[atom].vx
                vy += self.originalAtoms[atom].vy * self.currentAtoms[atom].vy
                vz += self.originalAtoms[atom].vz * self.currentAtoms[atom].vz
                
            self.velacf += vx+vy+vz
            self.velacf /= self.NumberOfAtoms*self.velacfinit
            self.velaclist.append(self.velacf)
            self.velacf = 0
                
    def getVAC(self):
        return self.velaclist
    
    def plotRDF(self):
        pass
        rdf=np.loadtxt("rdf.cvs")
        for radius in range(0,50):
            self.radUpdList.append(radius*self.dr)
        plt.figure()
        plt.plot(self.radUpdList,rdf)
        plt.show()
        
    def plotVAC(self,nSteps):
        pass
        vac = np.loadtxt("vac.cvs")
        vac[0] = 1
        for time in range(0,nSteps):
            self.timeUpdList.append(float(time)*self.dt)
        plt.figure()
        plt.plt(self.timeUpdList, vac)
        plt.show()
        
    def plotEnergy(self,temperatures, potentials,nSteps):
        """plots the kinetic, potential and total enegy of the system"""
        KE = []
        for temp in temperatures:
            KE.append(3*self.NumberOfAtoms*self.kb*temp/2)
        
        #Generate a list of steps
        stepList = []
        for time in range(0,nSteps):
            stepList.append(float(time))
        
        #Total ebergy function
        etot=[]
        for energy in range(0,nSteps):
            etot.append(KE[energy]+potentials[energy])
            
        plt.figure()
        plt.plt(stepList, KE, stepList, potentials, stepList,etot)
        plt.show()
        
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------        
#------------------------------------------------------------------------------  
nSteps=10  
sim=Simulation()
wf= writeFile()
analysis = Analysis(sim.getAtoms())
#
for step in range(0,nSteps):
    sim.runSimulation(step,nSteps)
    analysis.updateAtoms(sim.getAtoms())
    analysis.velAutocorrelation(step)
    wf.writeXYZ(sim.getAtoms())
    
wf.writeData("rdf.cvs", analysis.pairDistFunc())
wf.writeData("vac.cvs", analysis.getVAC())

analysis.pltRDF()
analysis.pltVAC(nSteps)
analysis.plotEnergy(sim.potentials,nSteps)