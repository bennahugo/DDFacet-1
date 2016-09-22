import numpy as np

def CatToFreqs(cat,fmin=0,fmax=-1,nf=0):


    #cat=np.load("cat_test.npy")
    #cat=cat.view(np.recarray)
    indsort=np.argsort(cat.Freq)
    cat=cat[indsort]
    keep=np.arange(cat.shape[0])

    #cat.Freq/=1.e6

    if fmin==0:
        fmin=np.min(cat.Freq)
    if fmax==-1:
        fmax=np.max(cat.Freq)
    if nf==0:
        nf=cat.shape[0]

    indf=np.where((cat.Freq<=fmax)&(cat.Freq>=fmin))[0]
    cat=cat[indf]
    
    fMS=cat.Freq
    dfMS=np.min(np.abs(fMS[1::]-fMS[0:-1]))


    fTarget=np.linspace(fmin,fmax,nf)
    dfTarget=fTarget[1]-fTarget[0]
    dnCompleteMS=int(round(dfTarget/dfMS))

    fCompleteMS=np.arange(fMS.min(),fMS.max(),dfMS)
    ifCompleteMS=np.arange(fCompleteMS.size)

    indSelCat=[]
    indTarget=[]
    fSelCat=[]
    fTarget=[]

    for i,fi in zip(ifCompleteMS[::dnCompleteMS],fCompleteMS[::dnCompleteMS]):
        d=np.abs(fi-fMS)
        idmin=np.argmin(d)
        dmin=d[idmin]
        indTarget.append(i)
        fTarget.append(fi)

        if dmin<.01e6:
            fSelCat.append(fMS[idmin])
            indSelCat.append(idmin)
        else:
            fSelCat.append(-1)
            indSelCat.append(idmin)
            print "point at i = %i, with fTarget = %f not found"%(i,fi)

    indSelCat=np.array(indSelCat)
    fSelCat=np.array(fSelCat)
    fTarget=np.array(fTarget)
    indTarget=np.array(indTarget)

    indfound=np.where(fSelCat!=-1)[0]

    cat=cat[indSelCat[np.array(indfound)]]
    fMS=cat.Freq
    dfMS=np.abs(fMS[1::]-fMS[0:-1])

    
    #print dfMS

            
            
    # import pylab
    # pylab.ion()
    # pylab.clf()
    # pylab.plot(ifCompleteMS,fCompleteMS,ls="",marker=".")
    # pylab.plot(indTarget,fTarget,ls="",marker=".",mew=5)#indSelCat,fSelCat)
    # pylab.plot(indTarget[indfound],fSelCat[indfound],ls="",marker=".")

    # pylab.legend(("CompleteMS","Target","Found"),loc=2)
    # pylab.draw()
    # pylab.show(False)


    return cat#,fTarget

    # Nchan=np.max(self.CatEngines.NChan)
    # Nbands=freqs.size/Nchan
    # freqs=freqs.reshape((Nbands,Nchan))
    # self.freqs=freqs
    # self.dfreq=dfreq