import random
import pandas as pd
from jmetal.core.problem import PermutationProblem
from jmetal.core.solution import PermutationSolution
from jmetal.operator import PMXCrossover, PermutationSwapMutation
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.termination_criterion import StoppingByEvaluations

class RoomAssignmentProblem(PermutationProblem):

    def name(self) -> str:
        return 'Room Assignment Problem'

    def number_of_constraints(self) -> int:
        return 0

    def number_of_objectives(self) -> int:
        return self.number_of_objectives

    def number_of_variables(self) -> int:
        return self.number_of_variables

    def __init__(self, rooms_df: pd.DataFrame, schedule_df: pd.DataFrame):
        super(RoomAssignmentProblem, self).__init__()
        self.rooms_df = rooms_df
        self.schedule_df = schedule_df

        self.number_of_variables = len(schedule_df)
        self.number_of_objectives = 2  # Example: minimize distance, balance usage
        self.number_of_constraints = 0  # No constraints

        self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['Total Distance', 'Balance Usage']

    def evaluate(self, solution: PermutationSolution):
        total_distance = 0
        room_usage = [0] * len(self.rooms_df)

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            room_index = solution.variables[i]
            room_info = self.rooms_df.iloc[room_index]

            # Placeholder: Calculate total distance (modify as needed)
            total_distance += abs(room_index - i)

            # Update room usage
            room_usage[room_index] += 1

        # Objective: Balance room usage
        balance_usage = max(room_usage) - min(room_usage)

        solution.objectives[0] = total_distance
        solution.objectives[1] = balance_usage

    def create_solution(self):
        solution = PermutationSolution(
            number_of_variables=self.number_of_variables,
            number_of_objectives=self.number_of_objectives,
            number_of_constraints=self.number_of_constraints
        )
        solution.variables = random.sample(range(len(self.rooms_df)), self.number_of_variables)
        return solution

# Assuming rooms_df and schedule_df are your DataFrames with the necessary data
schedule_df = pd.read_csv('testeHorario.csv', delimiter=';')
rooms_df = pd.read_csv('CaracterizaçãoDasSalas.csv', delimiter=';')

problem = RoomAssignmentProblem(rooms_df, schedule_df)

# Define the crossover and mutation operators
crossover_operator = PMXCrossover(probability=0.9)
mutation_operator = PermutationSwapMutation(probability=0.1)

# Define the algorithm
algorithm = GeneticAlgorithm(
    problem=problem,
    population_size=100,
    offspring_population_size=100,
    mutation=mutation_operator,
    crossover=crossover_operator,
    termination_criterion=StoppingByEvaluations(max_evaluations=1000)
)

progress_bar = ProgressBarObserver(max=100)
algorithm.observable.register(progress_bar)

# Run the algorithm
algorithm.run()

# Get the results
solution = algorithm.get_result()

print('Solution:', solution.variables)
print('Objectives:', solution.objectives)
