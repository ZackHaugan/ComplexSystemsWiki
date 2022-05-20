from re import X
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import scipy.special as special
import scipy.optimize as opt


# import WikiNetwork as dataframe
df = pd.read_csv('WikiNetwork.csv')

maxDegree = df["indegree"].max()
degrees = [0 for i in range(maxDegree + 1)]

for i in range(len(df.index)):
    degrees[df.iloc[i]['indegree']] += 1

for i in range(maxDegree + 1):
    degrees[i] /= len(df.index)


print("Average Indegree: ", df["indegree"].mean())
print("Average Outdegree: ", df["outdegree"].mean())
print("Average Degree: ", df["Degree"].mean())

averageDegree = df["indegree"].mean()
averageSquareDegree = sum(((index) ** 2) * (degree) for index, degree in enumerate(degrees))
variance = averageSquareDegree - (averageDegree ** 2)
standardDeviation = variance ** 0.5

print("Average Square Degree: ", averageSquareDegree)
print("Variance: ", averageSquareDegree - averageDegree ** 2)

neighborDegreeProbability = []
for i in range(maxDegree):
    neighborDegree = i + 1
    probability = ((neighborDegree + 1) * degrees[neighborDegree]) / averageDegree
    neighborDegreeProbability.append(probability)

averageNeighborDegree = sum([(i + 1) * neighborDegreeProbability[i] for i in range(len(neighborDegreeProbability))])

print("Average Neighbor Degree: ", averageNeighborDegree)


def gammDist(x, a, b):
    numerator = x**(a - 1) * np.exp(-b * x) * b ** a
    denominator = special.gamma(a)
    return numerator / denominator

popt, pcov = opt.curve_fit(gammDist, [(i) for i in range(maxDegree + 1)], degrees, bounds=((1e-9, 1e-9), (np.inf, np.inf)), p0=[averageDegree, averageDegree], method='trf')

print("Alpha: ", popt[0])
print("Beta: ", popt[1])

gammafit = gammDist(np.arange(maxDegree + 1), *popt)



plt.figure()

plt.scatter(np.arange(maxDegree + 1), degrees, 0.5)
plt.plot(np.arange(maxDegree + 1), gammafit, 'r-')


# print(fitData)

# plt.axvline(x=averageDegree + 2 * standardDeviation, color='r')
# plt.axvline(x=averageDegree - 2 * standardDeviation, color='r')
# plt.axvline(x=averageDegree, color='b')

plt.show()

