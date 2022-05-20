import numpy as np
import scipy.special as special
import pandas as pd

df = pd.read_csv('WikiNetwork.csv')

maxDegree = df["indegree"].max()


def gammDist(x, a, b):
    numerator = x**(a - 1) * np.exp(-b * x) * b ** a
    denominator = special.gamma(a)
    return numerator / denominator

a = 1.64921499401373
b = 0.0684938086058945

coefficients = []

for i in range(maxDegree + 1):
    coefficients.append(gammDist(i, a, b))

derCoefficients = [i * coef for i, coef in enumerate(coefficients)]
averageDegree = sum(derCoefficients)
averageSquareDegree = sum(((i) ** 2) * coef for i, coef in enumerate(coefficients))
variance = averageSquareDegree - (averageDegree ** 2)

print("Average Degree: ", averageDegree)
print("Average Square Degree: ", averageSquareDegree)
print("Variance: ", variance)

neighborProbability = []
for i in range(maxDegree):
    neighborDegree = i + 1
    probability = ((neighborDegree + 1) * coefficients[neighborDegree]) / averageDegree
    neighborProbability.append(probability)

averageNeighborDegree = sum([(i + 1) * neighborProbability[i] for i in range(len(neighborProbability))])

print("Average Neighbor Degree: ", averageNeighborDegree)
