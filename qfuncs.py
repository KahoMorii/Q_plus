import numpy as np
from scipy.sparse.csgraph import minimum_spanning_tree
import re
from scipy.spatial import KDTree

#===========================================================

    
def find_square(grid,p1,p2):
    for i in range(len(grid)):
        gs=grid[i]
        if (gs.pc1min<p1 and gs.pc1max>p1):
            if (gs.pc2min<p2 and gs.pc2max>p2):
                return i,gs.N
    


def find_c(testD,testG,A_val):
    c_file="./AllStars/C_D%3.2fG%i.res"%(testD,testG)
    arr=np.loadtxt(c_file,ndmin=2)
    cs=[]
    ps=[]
    for i in range(len(arr)):
        cs.append(1./arr[i,0])
        m=arr[i,1]
        s=arr[i,2]
        ps.append(normgaus(A_val,m,s))
    expect=sum(np.array(ps)*np.array(cs))/sum(ps)
    var=sum(np.array(ps)*pow((np.array(cs)-expect),2))/sum(ps)
    return expect,var
    
    
def find_neighbs(grid,i):
    this=grid[i]
    dx=this.pc1max-this.pc1min
    dy=this.pc2max-this.pc2min
    xmid=this.pc1min+0.5*dx
    ymid=this.pc2min+0.5*dy
    try:
        n1,nn1=find_square(grid,xmid-dx,ymid+dy)
    except TypeError:
        n1=0
        nn1=0
        pass
    try:
        n2,nn2=find_square(grid,xmid,ymid+dy)
    except TypeError:
        n2=0
        nn2=0
        pass
    try:
        n3,nn3=find_square(grid,xmid+dx,ymid+dy)
    except TypeError:
        n3=0
        nn3=0
        pass
    try:
        n4,nn4=find_square(grid,xmid-dx,ymid)
    except TypeError:
        n4=0
        nn4=0
        pass
    try:
        n5,nn5=find_square(grid,xmid+dx,ymid)
    except TypeError:
        n5=0
        nn5=0
        pass
    try:
        n6,nn6=find_square(grid,xmid-dx,ymid-dy)
    except TypeError:
        n6=0
        nn6=0
        pass
    try:
        n7,nn7=find_square(grid,xmid,ymid-dy)
    except TypeError:
        n7=0
        nn7=0
        pass
    try:
        n8,nn8=find_square(grid,xmid+dx,ymid-dy)
    except TypeError:
        n8=0
        nn8=0
        pass
    mask_empty_squares=np.array([nn1,nn2,nn3,nn4,nn5,nn6,nn7,nn8])
    n_tot=sum(mask_empty_squares)
    return np.array([n1,n2,n3,n4,n5,n6,n7,n8])[mask_empty_squares>0],n_tot

def pooledmeanvar(x,y):
    '''calculates mean and variance of hte combination of two data sets, x and y'''
    xmean = x[0]
    xvar  = x[1]
    ymean = y[0]
    yvar  = y[1]
    xn    = x[2] #number of points
    yn    = y[2]
    
    xyn    = xn + yn
    xymean = (xn * xmean + yn * ymean) / xyn
    xyvar  = np.sqrt(((xn * xvar**2 + yn * yvar**2)/xyn) + ((xn * yn)/(xyn**2))*((xmean - ymean)**2))
    
    return xymean, xyvar, xyn


def get_parameter_space():
    F = np.array([2.0, 3.0, 4.0, 5.0]) #ax0
    C = np.array([2.0, 3.0, 22.0]) #ax1
    G = np.array([3.0, 4.0, 5.0, 6.0, 7.0, 8.0]) #ax2
    D=np.log2(F)
    
    return D,C,G,F

def rotate_view(stars):
    relev=np.random.uniform(-90,90)
    razim=np.random.uniform(0,360)
    phi=np.deg2rad(relev)
    theta=np.deg2rad(razim)
    T1=np.array([[-np.sin(phi), 0, -np.cos(phi)],
                   [0, 1, 0],
                   [np.cos(phi), 0, -np.sin(phi)]])
    T2=np.array([[np.cos(theta), np.sin(theta), 0],
                   [-np.sin(theta), np.cos(theta), 0],
                   [0, 0, 1]])
    T=np.dot(T1,T2)
    poss=[]
    for (X,Y,Z) in stars:
        p=np.array([X,Y,Z])
        p_rot=np.dot(T,p)
        poss.append(p_rot)
    return poss

def cull2sphere(poss):
    star_poss_2=[]
    for s in poss:
        if s[0]**2+s[1]**2+s[2]**2<1.:
            star_poss_2.append(s)
    return star_poss_2

def writelist(out,l):
    out.writelines(["%s\t" % item  for item in l])
    out.write("\n")
    
def A_measure(edges,smax):
    eta=1
    edges.sort()
    m=np.array(edges)/smax
    n=len(m)
    A=m[0]*2**eta + m[n-1]*(n-1**eta - (n-2)**eta)
    for i in range(1,n-2):
        A+=m[i]*((i+1)**eta - (i-1)**eta)
    return A/(2.*n**eta)

def justMST(x,y,z=[8]):
    if len(z)==1: #2D data
        grid=np.zeros((len(x),len(y)))
        all_edges=[]
        for i in range(len(x)):
            for j in range(len(x)):
                if i!=j:
                    if grid[j][i]==0:
                        grid[i][j]=np.sqrt((x[i]-x[j])**2+(y[i]-y[j])**2)
                        all_edges.append(grid[i][j])   
        Tcsr = minimum_spanning_tree(grid,overwrite=True)
        mst=Tcsr.toarray().astype(float)
    
    elif len(z)==len(x):
        length=len(x)
        grid=np.zeros((length,length))
        all_edges=[]
        for i in range(length):
            for j in range(length):
                if i!=j:
                    if grid[j][i]==0:
                        grid[i][j]=np.sqrt((x[i]-x[j])**2+(y[i]-y[j])**2+(z[i]-z[j])**2)
                        all_edges.append(grid[i][j])   
        #make mst
        Tcsr = minimum_spanning_tree(grid,overwrite=True)
        mst=Tcsr.toarray().astype(float)
    else:
        print("Error: x,y, and z must have the same length")
        quit()
    return mst, all_edges
    
    
def makeMST(datafile,ucols=[0,1]):
    d,c,g,r=0,0,0,0
    #read in data
    with open(datafile, 'r') as infile:
        x,y=np.loadtxt(infile,skiprows=0,unpack=True,usecols=ucols)
    #basis statistics
    x,y=normstar(x,y)
    n_entries=len(x)
    R_cluster=np.amax(np.sqrt((x-np.mean(x))**2+(y-np.mean(y))**2))
    A_cluster=np.pi*pow(R_cluster,2)
    #make complete graph
    mst,all_edges=justMST(x,y)
    #make resultslist
    reslist=[]
    reslist.append(d)#D
    reslist.append(c)#C
    reslist.append(g)#G
    reslist.append(r)#R
    reslist.append(np.log10(n_entries))# log(n)
    all_edges.sort()
    reslist.append(np.log(all_edges[-1]/all_edges[4]))#Rmeasure
    reslist.append(A_measure(mst[mst!=0],all_edges[-1]))#Ameasure
    reslist.append((np.mean(mst[mst!=0])*(n_entries-1.))/pow((n_entries*A_cluster),0.5))#mbar
    reslist.append(np.mean(all_edges)/R_cluster)#sbar
    reslist.append(np.mean(mst[mst!=0]))#mean mst
    reslist.append(np.std(mst[mst!=0]))#std mst
    reslist.append(np.mean(all_edges))#mean all
    reslist.append(np.std(all_edges))#std all
    reslist.append(reslist[7]/reslist[8]) #Q parameter
    return reslist,x,y

def n_stars(d, c, g):
    #d = np.log2(dp)
    #c = 2.+(1./cp)
    alpha = pow(2., (c+d-3.))
    n0 = pow(2., (3.-c)*g)
    if (alpha-1. < 0.01):
        return n0*(g+1.)
    else:   
        return n0*(pow(alpha, (g+1.))-1.)/(alpha-1.)

def normgaus(val, mu, sig):
    #find prob of val being drawn from gaussian mu, sig
    if sig<0.001:
        sig=0.001
    normfac=1./(pow(2.*np.pi, 0.5)*sig)
    ex=np.exp(-((val-mu)**2)/(2.*(sig**2)))
    return normfac*ex
    
def gaus(val, mu, sig, A):
    #find prob of val being drawn from gaussian mu, sig
    ex=A*np.exp(-((val-mu)**2)/(2.*(sig**2)))
    return ex

    
def fit(val,name,stats):
    #print val,name,stats
    return normgaus(val, stats[name]['mu'], stats[name]['sig'])

def normstar(x,y,z=np.array([0])):
    ''' reads in 2d or 3d star cluster and normalises
    positions to radius of 1 centred on mean position'''
    
    xmean=np.mean(x)
    ymean=np.mean(y)
    
    x=x-xmean #centre on mean position
    y=y-ymean
    posmax=max(max(abs(x)),max(abs(y))) #find maximum distance from mean
    
    if len(z)>1:
        #3D cluster
        zmean=np.mean(z)
        z=z-zmean
        posmax=max(posmax,max(abs(z)))
    
    #Scale all positions to maximum distance from centre.
    invmax=1./posmax
    
    x=x*invmax
    y=y*invmax
    z=z*invmax
    
    if len(z)>1:
        return x,y,z
    else:
        return x,y

def cartesian(arrays, out=None):
    """
    Generate a cartesian product of input arrays.

    Parameters
    ----------
    arrays : list of array-like
        1-D arrays to form the cartesian product of.
    out : ndarray
        Array to place the cartesian product in.

    Returns
    -------
    out : ndarray
        2-D array of shape (M, len(arrays)) containing cartesian products
        formed of input arrays.

    Examples
    --------
    >>> cartesian(([1, 2, 3], [4, 5], [6, 7]))
    array([[1, 4, 6],
           [1, 4, 7],
           [1, 5, 6],
           [1, 5, 7],
           [2, 4, 6],
           [2, 4, 7],
           [2, 5, 6],
           [2, 5, 7],
           [3, 4, 6],
           [3, 4, 7],
           [3, 5, 6],
           [3, 5, 7]])

    """

    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    n = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([n, len(arrays)], dtype=dtype)

    # m = n / arrays[0].size
    m = n // arrays[0].size
    out[:,0] = np.repeat(arrays[0], m)
    if arrays[1:]:
        cartesian(arrays[1:], out=out[0:m,1:])
        for j in range(1, arrays[0].size):
            out[j*m:(j+1)*m,1:] = out[0:m,1:]
    return out
    
def select_data(full,d=99,c=99,g=99,dstring='D',cstring='C',gstring='G',sep=0.1):
    if d!=99:
        full=full[(abs(full[dstring]-d)<sep)]
    if c!=99:
        full=full[(abs(full[cstring]-c)<sep)]
    if g!=99:
        full=full[(abs(full[gstring]-g)<sep)]
    return full
    
def struct_to_array(struct):
    tmp=[]
    [ tmp.append(struct[col]) for col in struct.dtype.names]
    arr=np.array(tmp,dtype=float)
    return arr
    
def transform_to_pc(tdata,method='cov'):
                     
    #subtract means
    if method=='cov':
        tmp=np.load('fullmeans.npy')
        meanarr=struct_to_array(tmp)
        
        numarray=struct_to_array(tdata)
        meaned=np.zeros_like(numarray,dtype=float)
        
        for i in range(len(meanarr)):
            meaned[i,:]=(numarray[i,:]-meanarr[i])
            
        #multiply by eigenvecors
        eig=np.load('eigenfull.npz')
        evects=eig['evects'][:,:2]
        #print(meaned.shape)
        newData=np.dot(evects.T,meaned)
    elif method=='corr':
        tmp=np.load('new_fullmeans.npz')
        meanarr=struct_to_array(tmp['means'])
        stdarr=struct_to_array(tmp['stds'])
        
        numarray=struct_to_array(tdata)
        meaned=np.zeros_like(numarray,dtype=float)
        
        for i in range(len(meanarr)):
            meaned[i,:]=(numarray[i,:]-meanarr[i])/stdarr[i]
            
        #multiply by eigenvecors
        eig=np.load('new_eigen.npz')
        evects=eig['evects'][:,:2]
        newData=np.dot(evects.T,meaned)
    return newData

def find_binaries(x,y,z=[],v=0.03):
    if len(z)<1:
        data=np.vstack((x,y)).T
    else:
        data=np.vstack((x,y,z)).T
    #print data.T
    KDT=KDTree(data)
    #print "Tree made"
    binaries=list(KDT.query_pairs(v))
    #print binaries
    try:
        return binaries#[0]
    except IndexError:
        return []

def remove_binaries(x,y,z=[],scale=0.03,expected=0):
    if len(z)<1: #2D
        bins=find_binaries(x,y,v=scale)
        deleted_stars=[]
        while len(bins)>expected:
            #print bins
            i,j = bins[0]
            xa=x.pop(i)
            xb=x.pop(j-1)
            ya=y.pop(i)
            yb=y.pop(j-1)
            xn=(xa+xb)*0.5
            yn=(ya+yb)*0.5
            x.append(xn)
            y.append(yn)
            deleted_stars.extend([[xa,ya],[xb,yb]])
            bins=find_binaries(x,y,v=scale)
    else: #3D
        bins=find_binaries(x,y,z=z,v=scale)
        deleted_stars=[]
        while len(bins)>expected:
            #print bins
            i,j = bins[0] #index of binary pair
            xa=x.pop(i) #remove both from x,y,z
            xb=x.pop(j-1)
            ya=y.pop(i)
            yb=y.pop(j-1)
            za=z.pop(i)
            zb=z.pop(j-1)
            xn=(xa+xb)*0.5 #position of new "system"
            yn=(ya+yb)*0.5
            zn=(za+zb)*0.5
            x.append(xn) #add new system
            y.append(yn)
            z.append(zn)
            deleted_stars.extend([[xa,ya,za],[xb,yb,zb]])
            bins=find_binaries(x,y,z=z,v=scale)
    return x,y,z,deleted_stars
