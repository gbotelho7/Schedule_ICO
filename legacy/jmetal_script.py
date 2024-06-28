# jmetal_script.py
from jmetal.algorithm.multiobjective import NSGAII
from jmetal.operator import SBXCrossover, PolynomialMutation
from jmetal.problem import ZDT1
from jmetal.util.observer import PrintObjectivesObserver
from jmetal.util.termination_criterion import StoppingByEvaluations

def run_jmetal():
    problem = ZDT1()
    algorithm = NSGAII(
        problem=problem,
        population_size=100,
        offspring_population_size=100,
        mutation=PolynomialMutation(probability=1.0/problem.number_of_variables, distribution_index=20),
        crossover=SBXCrossover(probability=1.0, distribution_index=20),
        termination_criterion=StoppingByEvaluations(max_evaluations=25000)
    )

    algorithm.observable.register(observer=PrintObjectivesObserver(100))
    algorithm.run()
    front = algorithm.get_result()
    
    # Example: returning the first solution's objectives
    return front[0].objectives

if __name__ == "__main__":
    result = run_jmetal()
    print(result)