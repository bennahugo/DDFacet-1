#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import random

import numpy
import numpy as np

from deap import algorithms
import DeapAlgo as algorithms
from deap import base
from deap import creator
from deap import tools
import pylab
from scipy.spatial import Voronoi
import ModVoronoi

def test():
    Np=1000
    x=np.random.randn(Np)
    y=np.random.randn(Np)
    
    CC=ClassCluster(x,y)
    CC.Cluster()
    
def evalOneMax(individual):
    return sum(individual),


def cxTwoPointCopy(ind1, ind2):
    """Execute a two points crossover with copy on the input individuals. The
    copy is required because the slicing in numpy returns a view of the data,
    which leads to a self overwritting in the swap operation. It prevents
    ::
    
        >>> import numpy
        >>> a = numpy.array((1,2,3,4))
        >>> b = numpy.array((5.6.7.8))
        >>> a[1:3], b[1:3] = b[1:3], a[1:3]
        >>> print(a)
        [1 6 7 4]
        >>> print(b)
        [5 6 7 8]
    """
    size = len(ind1)
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else: # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] \
        = ind2[cxpoint1:cxpoint2].copy(), ind1[cxpoint1:cxpoint2].copy()
        
    return ind1, ind2

import Polygon


def doOverlap(npP0,npP1):
    P0 = Polygon.Polygon(npP0)
    P1 = Polygon.Polygon(npP1)
    P1Cut = (P0 & P1)
    aP1=P1.area()
    aP1Cut=P1Cut.area()
    if np.abs(aP1Cut-aP1)<1e-10 or aP1Cut==0:
        return False
    else:
        return True
    
def Mutate(Indiv,indpb=0.05):
    N=Indiv.size/2
    Ind=Indiv.reshape((2,N))
    #i=int(np.random.rand(1)[0]*N)
    for i in range(N):
        r=int(np.random.rand(1)[0]*N)
        if r>indpb: continue
        ra,dec=Ind
        ra[i]+=np.random.randn(1)[0]#*0.03
        dec[i]+=np.random.randn(1)[0]#*0.03
    return Indiv,
    
class ClassCluster():
    def __init__(self,x,y,nNode=50):
        self.x=x
        self.y=y
        self.nNode=nNode
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()
        toolbox.register("attr_float", random.uniform, -5, 5)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=2*nNode)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # toolbox.register("individual",
        #                  tools.initCycle,
        #                  creator.Individual,
        #                  Obj, n=1)
        # toolbox.register("population", tools.initRepeat, list, toolbox.individual)


        toolbox.register("evaluate", self.giveFitness)
        toolbox.register("mate", cxTwoPointCopy)
        #toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("mutate", Mutate, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        self.toolbox=toolbox

        self.Polygons=[np.array([[0,0],[0,1],[1,1.]])*0.5]

        
    def giveFitness(self,Indiv):
        xc,yc=Indiv.reshape((2,self.nNode))
        dx=xc.reshape((-1,1))-self.x.reshape((1,-1))
        dy=yc.reshape((-1,1))-self.y.reshape((1,-1))
        d=np.sqrt(dx**2+dy**2)
        ind=np.argmin(d,axis=0)
        II=np.unique(ind)
        NPerNode=np.zeros((xc.size,),np.float32)
        for iC in II:
            NPerNode[iC]=np.count_nonzero(ind==iC)

        fOverlap=0
        if self.Polygons is not None:
            xy=np.zeros((xc.size,2),np.float32)
            xy[:,0]=xc
            xy[:,1]=yc
            vor = Voronoi(xy)#incremental=True)
            regions, vertices = ModVoronoi.voronoi_finite_polygons_2d(vor)
            
            for region in regions:
                polygon = vertices[region]
                for P in self.Polygons:
                    fOverlap+=doOverlap(polygon,P)
                    

            
        std=-np.std(NPerNode)+(-np.count_nonzero(NPerNode==0)*1e2)-fOverlap*1e5
        return std,

            
    def Cluster(self):
        random.seed(64)
        toolbox=self.toolbox
        pop = toolbox.population(n=1000)
        
        # Numpy equality function (operators.eq) between two arrays returns the
        # equality element wise, which raises an exception in the if similar()
        # check of the hall of fame. Using a different equality function like
        # numpy.array_equal or numpy.allclose solve this issue.
        hof = tools.HallOfFame(1, similar=numpy.array_equal)
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        PlotMachine=ClassPlotMachine(self.x,self.y,self.Polygons)
        algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=1000, stats=stats,
                            halloffame=hof,PlotMachine=PlotMachine)

        return pop, stats, hof

class ClassPlotMachine():
    def __init__(self,x,y,Polygons=None):
        self.x=x
        self.y=y
        self.Polygons=Polygons

    def Plot(self,hof):
        indiv=hof[-1]
        N=indiv.size/2
        xc,yc=indiv.reshape((2,N))

        xc,yc=indiv.reshape((2,N))
        xy=np.zeros((xc.size,2),np.float32)
        xy[:,0]=xc
        xy[:,1]=yc
        vor = Voronoi(xy)#incremental=True)
        
        regions, vertices = ModVoronoi.voronoi_finite_polygons_2d(vor)



        dx=xc.reshape((-1,1))-self.x.reshape((1,-1))
        dy=yc.reshape((-1,1))-self.y.reshape((1,-1))
        d=np.sqrt(dx**2+dy**2)
        ind=np.argmin(d,axis=0)

        pylab.clf()
        pylab.subplot(1,2,1)
        for region in regions:
            polygon = vertices[region]
            pylab.fill(*zip(*polygon), alpha=0.4)
            dx=0.01
            pylab.xlim(self.x.min() - dx, self.x.max()+dx)
            pylab.ylim(self.y.min() - dx, self.y.max()+dx)
        pylab.scatter(self.x,self.y,c=ind,s=5)
        pylab.scatter(xc,yc,color="red")

        if self.Polygons is not None:
            xp,yp=self.Polygons[0].T
            pylab.fill(*zip(*self.Polygons[0]), alpha=0.4)

            #pylab.plot(xp,yp)

        II=np.unique(ind)
        NPerNode=np.zeros((xc.size,),np.float32)
        for iC in II:
            NPerNode[iC]=np.count_nonzero(ind==iC)

        pylab.subplot(1,2,2)
        pylab.hist(NPerNode,bins=100)

        pylab.pause(0.1)
        pylab.draw()
        pylab.show(False)
        
        # II=np.unique(ind)
        # NPerNode=np.zeros((xc.size,),np.float32)
        # for iC in II:
        #     NPerNode[iC]=np.count_nonzero(ind==iC)

            
