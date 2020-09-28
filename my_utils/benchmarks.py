
import math
def shwefels(dna):
    total=0
    for i in range(len(dna)):
       total += dna[i]*math.sin(math.sqrt(abs(dna[i])))
    return (418.9829*len(dna))-total        
def sphere(dna):
    total = 0
    for i in dna:
        total+=i**2
    return total
def rosenbrock(dna):
    total = 0
    for i in range(len(dna)-1):
        x = 100
        x*=(dna[i+1]-(dna[i]**2))**2
        x+=(dna[i]-1)**2
        total+=x
    return total
def ackley(dna):
    n = len(dna)
    sxi2 = 0
    cosm = 0
    for i in dna:
        sxi2+=i**2
        cosm+=math.cos((2*math.pi)*i)
    sxi2 = 20*math.exp(-0.2*math.sqrt((1/n)*sxi2))
    cosm = math.exp((1/n)*cosm)
    return 20 + math.e - sxi2 - cosm
def rastrigin(dna):
    sm = 0
    for i in dna:
        sm+=(i**2)-(10*math.cos(math.pi*2*i))
    return (10*len(dna))+sm
def griewank(dna):
    sm =0
    prod = 1
    for i in range(len(dna)):
        sm+=dna[i]**2
        prod *=math.cos(dna[i]/math.sqrt((i+1)))
    sm*=1/4000
    return (1+sm)-prod 