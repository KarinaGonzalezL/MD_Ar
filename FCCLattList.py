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

# comment

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#---------------Useful classes------------------------------------------------
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Atom(object):
    def __init__(self):
        self.x,self.y,self.z=0,0,0
        self.vx,self.vy,self.vz=0,0,0
        self.fx,self.fy,self.vz=0,0,0
        self.potential = 0
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++                     
class Simulation:
    
    rho = 0.3                       # density
    
    NumberOfAtoms = 108
    L = (NumberOfAtoms/rho)**(1/3.0)    # length of box
    print(L)
    atoms= []

    
    print("EmpiezalaclaseSimulacion")  
    def __init__(self):
        """Creates a simulation with NumberOfAtoms"""
        print("initializing system...")
        for i in range(0,self.NumberOfAtoms):
            self.atoms.append(Atom())
        self.assignPositions()
        print("Done")
        print("Simulation is runnning")

        
    def assignPositions(self):
        Nc = int((self.NumberOfAtoms/4)**(1/3))   #Calculate number of unit cells in each direction
        print(Nc)

        
        fig = plt.figure()
        ax = p3.Axes3D(fig)
        #Initialize the initial positions based on fcc stacking        
#        self.r = np.zeros((3, self.NumberOfAtoms) )            
        particle=0
        for x in range(Nc):
            for y in range(Nc):
                for z in range(Nc):
                    self.atoms[particle].x = x*self.L/Nc
                    self.atoms[particle].y = y*self.L/Nc
                    self.atoms[particle].z = z*self.L/Nc
                    particle +=1
                    self.atoms[particle].x = x*self.L/Nc 
                    self.atoms[particle].y = y*self.L/Nc + 0.5*self.L/Nc
                    self.atoms[particle].z = z*self.L/Nc + 0.5*self.L/Nc
                    particle +=1
                    self.atoms[particle].x = x*self.L/Nc + 0.5*self.L/Nc
                    self.atoms[particle].y = y*self.L/Nc 
                    self.atoms[particle].z = z*self.L/Nc + 0.5*self.L/Nc
                    particle +=1
                    self.atoms[particle].x = x*self.L/Nc + 0.5*self.L/Nc
                    self.atoms[particle].y = y*self.L/Nc + 0.5*self.L/Nc
                    self.atoms[particle].z = z*self.L/Nc
                    particle +=1
                                
                    R=np.array([self.atoms[particle].x,self.atoms[particle].y,self.atoms[particle].z])
        for atom in range(particle):
            #Center the particles (so they aren't at the boundary)
            self.atoms[atom].x += self.L/Nc/4   
            self.atoms[atom].y += self.L/Nc/4
            self.atoms[atom].z += self.L/Nc/4 
            
        ax.scatter(R[0],R[1],R[2], "-")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
    plt.show()
        

