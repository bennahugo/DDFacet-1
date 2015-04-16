
from pyrap.images import image
import os
from DDFacet.Other import MyPickle
import numpy as np
from DDFacet.Other import MyLogger
log=MyLogger.getLogger("ClassCasaImage")
from DDFacet.ToolsDir import rad2hmsdms
import pyfits
import pyrap.images

class ClassCasaimage():
    def __init__(self,ImageName,ImShape,Cell,radec,KeepCasa=False):
        self.Cell=Cell
        self.radec=radec
        self.KeepCasa=KeepCasa

        self.ImShape=ImShape
        self.nch,self.npol,self.Npix,_=ImShape

        self.ImageName=ImageName
        #print "image refpix:",rad2hmsdms.rad2hmsdms(radec[0],Type="ra").replace(" ",":"),", ",rad2hmsdms.rad2hmsdms(radec[1],Type="dec").replace(" ",".")
        self.createScratch()

    def create(self):
        ImageName=self.ImageName
        #print>>log, "  ----> Create casa image %s"%ImageName
        HYPERCAL_DIR=os.environ["HYPERCAL_DIR"]
        c=MyPickle.Load("%s/pythonlibs/CoordCasa.pickle"%HYPERCAL_DIR)
        incr=c.get_increment()
        incrRad=(self.Cell/60.)#*np.pi/180
        incr[0][0]=incrRad
        incr[0][1]=-incrRad
        c.set_increment(incr)
        RefPix=c.get_referencepixel()
        Npix=self.Npix
        #RefPix[0][0]=Npix/2
        #RefPix[0][1]=Npix/2

        RefPix[0][0]=Npix/2-1
        RefPix[0][1]=Npix/2-1

        RefPix=c.set_referencepixel(RefPix)
        RefVal=c.get_referencevalue()
        RaDecRad=self.radec
        RefVal[0][1]=RaDecRad[0]*180./np.pi*60
        RefVal[0][0]=RaDecRad[1]*180./np.pi*60
        RefVal=c.set_referencevalue(RefVal)
        os.system("rm -Rf %s"%ImageName)
        #self.im=image(imagename=ImageName,shape=(1,1,Npix,Npix),coordsys=c)
        self.im=image(imagename=ImageName,shape=(Npix,Npix),coordsys=c)
        
    def createScratch(self):
        ImageName=self.ImageName
        #print>>log, "  ----> Create casa image %s"%ImageName
        #HYPERCAL_DIR=os.environ["HYPERCAL_DIR"]
        tmpIm=image(imagename=ImageName,shape=self.ImShape)
        c=tmpIm.coordinates()
        del(tmpIm)
        os.system("rm -Rf %s"%ImageName)

        incr=c.get_increment()
        incrRad=(self.Cell/60.)#*np.pi/180
        incr[-1][0]=incrRad
        incr[-1][1]=-incrRad
        c.set_increment(incr)
        #RefPix=c.get_referencepixel()
        Npix=self.Npix
        #RefPix[0][0]=Npix/2
        #RefPix[0][1]=Npix/2

        #RefPix[0][0]=Npix/2-1
        #RefPix[0][1]=Npix/2-1

        #RefPix=c.set_referencepixel(RefPix)
        RefVal=c.get_referencevalue()
        RaDecRad=self.radec
        RefVal[-1][1]=RaDecRad[0]*180./np.pi*60
        RefVal[-1][0]=RaDecRad[1]*180./np.pi*60
        RefVal=c.set_referencevalue(RefVal)
        #self.im=image(imagename=ImageName,shape=(1,1,Npix,Npix),coordsys=c)
        #self.im=image(imagename=ImageName,shape=(Npix,Npix),coordsys=c)
        self.im=image(imagename=ImageName,shape=self.ImShape,coordsys=c)
        #data=np.random.randn(*self.ImShape)
        #self.setdata(data)
        
    def setdata(self,dataIn,CorrT=False):
        #print>>log, "  ----> put data in casa image %s"%self.ImageName

        data=dataIn.copy()
        if CorrT:
            nch,npol,_,_=dataIn.shape
            for ch in range(nch):
                for pol in range(npol):
                    data[ch,pol]=data[ch,pol][::-1].T
        
        self.im.putdata(data)

    def ToFits(self):
        FileOut=self.ImageName+".fits"
        os.system("rm -rf %s"%FileOut)
        print>>log, "  ----> Save data in casa image as FITS file %s"%FileOut
        self.im.tofits(FileOut)

    def setBeam(self,beam):
        bmaj, bmin, PA=beam
        FileOut=self.ImageName+".fits"
        #print>>log, "  ----> Save beam info in FITS file %s"%FileOut
        
        F2=pyfits.open(FileOut)
        F2[0].header["BMAJ"]=bmaj
        F2[0].header["BMIN"]=bmin
        F2[0].header["BPA"]=PA
        os.system("rm -rf %s"%FileOut)
        F2.writeto(FileOut,clobber=True)


    def close(self):
        #print>>log, "  ----> Closing %s"%self.ImageName
        del(self.im)
        #print>>log, "  ----> Closed %s"%self.ImageName
        if self.KeepCasa==False:
            #print>>log, "  ----> Delete %s"%self.ImageName
            os.system("rm -rf %s"%self.ImageName)




# def test():

#     ra=15.*(2.+30./60)*np.pi/180
#     dec=(40.+30./60)*np.pi/180
    
#     radec=(ra,dec)
#     Cell=20.
#     imShape=(1, 1, 1029, 1029)
#     #name="lala2.psf"
#     name,imShape,Cell,radec="lala2.psf", (1, 1, 1029, 1029), 20, (3.7146787856873478, 0.91111035090915093)

#     im=ClassCasaimage(name,imShape,Cell,radec)
#     im.setdata(np.random.randn(*(imShape)),CorrT=True)
#     im.ToFits()
#     im.setBeam((0.,0.,0.))
#     im.close()

def test():
    name,imShape,Cell,radec="lala2.psf", (1, 1, 1029, 1029), 20, (3.7146787856873478, 0.91111035090915093)
    im=ClassCasaimage(name,imShape,Cell,radec)
    im.setdata(np.random.randn(*(imShape)),CorrT=True)
    im.ToFits()
    im.setBeam((0.,0.,0.))
    im.close()

if __name__=="__main__":
    test()
