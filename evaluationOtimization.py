# import matplotlib.pyplot as plt

# # Defining the Solution class to store the solutions
# class Solution:
#     def __init__(self, objective1, objective2):
#         self.objective1 = objective1
#         self.objective2 = objective2

# # Creating the solutions list
# solutions1 = [
#     Solution(17, 27),
#     Solution(19, 25),
#     Solution(18, 26),
#     Solution(21, 25),
#     Solution(19, 26),
#     Solution(19, 26),
#     Solution(18, 27),
#     Solution(19, 26),
#     Solution(19, 26),
#     Solution(18, 27),
#     Solution(18, 27),
#     Solution(24, 25),
#     Solution(20, 26),
#     Solution(20, 26),
#     Solution(20, 26),
#     Solution(20, 26),
#     Solution(20, 26),
#     Solution(19, 27),
#     Solution(20, 27),
#     Solution(21, 27)
# ]

# # Extracting the objectives for plotting
# objective1 = [sol.objective1 for sol in solutions1]
# objective2 = [sol.objective2 for sol in solutions1]

# # Plotting the solutions with extended axis intervals
# plt.figure(figsize=(12, 8))
# plt.scatter(objective1, objective2, color='blue')
# plt.title('Multi-objective Optimization Results', fontsize=16)
# plt.xlabel('Objective 1', fontsize=14)
# plt.ylabel('Objective 2', fontsize=14)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)
# plt.grid(True)
# plt.xlim(10, 30)
# plt.ylim(10, 30)
# plt.show()


import matplotlib.pyplot as plt
import numpy as np

# Definindo a classe Solution para armazenar as soluções
class Solution:
    def __init__(self, objective1, objective2):
        self.objective1 = objective1
        self.objective2 = objective2

# Criando a lista de soluções
solutions1 = [
    Solution(17, 27),
    Solution(19, 25),
    Solution(18, 26),
    Solution(21, 25),
    Solution(19, 26),
    Solution(19, 26),
    Solution(18, 27),
    Solution(19, 26),
    Solution(19, 26),
    Solution(18, 27),
    Solution(18, 27),
    Solution(24, 25),
    Solution(20, 26),
    Solution(20, 26),
    Solution(20, 26),
    Solution(20, 26),
    Solution(20, 26),
    Solution(19, 27),
    Solution(20, 27),
    Solution(21, 27)
]

# Extraindo os objetivos para plotagem
objective1 = [sol.objective1 for sol in solutions1]
objective2 = [sol.objective2 for sol in solutions1]

# Gráfico de Dispersão
plt.figure(figsize=(12, 8))
plt.scatter(objective1, objective2, color='blue')
plt.title('Multi-objective Optimization Results', fontsize=16)
plt.xlabel('Objective 1', fontsize=14)
plt.ylabel('Objective 2', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)
plt.xlim(10, 30)
plt.ylim(10, 30)
plt.show()

# Identificação da fronteira de Pareto
def pareto_frontier(obj1, obj2, maxX = True, maxY = True):
    sorted_list = sorted([[obj1[i], obj2[i]] for i in range(len(obj1))], reverse=maxX)
    p_front = [sorted_list[0]]    
    for pair in sorted_list[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:
                p_front.append(pair)
        else:
            if pair[1] <= p_front[-1][1]:
                p_front.append(pair)
    return np.array(p_front)

# Obtendo a fronteira de Pareto
pareto = pareto_frontier(objective1, objective2, maxX=False, maxY=True)

# Gráfico de Dispersão com Fronteira de Pareto
plt.figure(figsize=(12, 8))
plt.scatter(objective1, objective2, color='blue', label='Solutions')
plt.plot(pareto[:, 0], pareto[:, 1], color='red', linestyle='--', marker='o', label='Pareto Frontier')
plt.title('Pareto Frontier', fontsize=16)
plt.xlabel('Objective 1', fontsize=14)
plt.ylabel('Objective 2', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
plt.grid(True)
plt.xlim(10, 30)
plt.ylim(10, 30)
plt.show()

# Boxplot para Objective 1
plt.figure(figsize=(12, 8))
plt.boxplot(objective1)
plt.title('Boxplot of Objective 1', fontsize=16)
plt.ylabel('Value', fontsize=14)
plt.xticks([1], ['Objective 1'], fontsize=12)
plt.grid(True)
plt.show()

# Boxplot para Objective 2
plt.figure(figsize=(12, 8))
plt.boxplot(objective2)
plt.title('Boxplot of Objective 2', fontsize=16)
plt.ylabel('Value', fontsize=14)
plt.xticks([1], ['Objective 2'], fontsize=12)
plt.grid(True)
plt.show()

# Histograma para Objective 1
plt.figure(figsize=(12, 8))
plt.hist(objective1, bins=10, color='blue', alpha=0.7)
plt.title('Histogram of Objective 1', fontsize=16)
plt.xlabel('Value', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(True)
plt.show()

# Histograma para Objective 2
plt.figure(figsize=(12, 8))
plt.hist(objective2, bins=10, color='blue', alpha=0.7)
plt.title('Histogram of Objective 2', fontsize=16)
plt.xlabel('Value', fontsize=14)
plt.ylabel('Frequency', fontsize=14)
plt.grid(True)
plt.show()
