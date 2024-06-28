import pandas as pd
from jmetal.core.problem import PermutationProblem
from jmetal.core.solution import PermutationSolution
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator import PermutationSwapMutation, PMXCrossover, CXCrossover, NullCrossover
from jmetal.util.termination_criterion import StoppingByEvaluations
import random

class RoomAssignmentProblem(PermutationProblem):
    def name(self) -> str:
        return 'Room Assignment Problem'

    def number_of_constraints(self) -> int:
        return 1

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
        self.number_of_constraints = 1  # Example: room capacity constraint

        self.lower_bound = [0] * self.number_of_variables
        self.upper_bound = [len(rooms_df) - 1] * self.number_of_variables

        self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['Total Distance', 'Balance Usage']

    def evaluate(self, solution: PermutationSolution):
        total_distance = 0
        room_usage = [0] * len(self.rooms_df)

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            room_index = solution.variables[i]
            room_info = self.rooms_df.iloc[room_index]

            # Constraint: Room capacity
            if room_info['Capacidade Normal'] < class_info['Inscritos no turno']:
                solution.constraints[0] = -1
                return

            # Placeholder: Calculate total distance (modify as needed)
            total_distance += abs(room_index - i)

            # Update room usage
            room_usage[room_index] += 1

        # Objective: Balance room usage
        balance_usage = max(room_usage) - min(room_usage)

        solution.objectives[0] = total_distance
        solution.objectives[1] = balance_usage
        solution.constraints[0] = 0

    def create_solution(self):
        solution = PermutationSolution(
            number_of_variables=self.number_of_variables,
            number_of_objectives=self.number_of_objectives,
            number_of_constraints=self.number_of_constraints
        )
        solution.variables = [random.randint(self.lower_bound[i], self.upper_bound[i]) for i in
                              range(self.number_of_variables)]
        return solution


schedule_df = pd.read_csv('../testeHorario.csv', delimiter=';')
rooms_df = pd.read_csv('../CaracterizaçãoDasSalas.csv', delimiter=';')

# Define the problem
problem = RoomAssignmentProblem(rooms_df=rooms_df, schedule_df=schedule_df)

# Configure the algorithm
algorithm = NSGAII(
    problem=problem,
    population_size=100,
    offspring_population_size=100,
    mutation=PermutationSwapMutation(probability=0.1),
    crossover=PMXCrossover(probability=0.9),
    # crossover=CXCrossover(probability=0.9),
    # crossover=NullCrossover(),
    termination_criterion=StoppingByEvaluations(max_evaluations=10000)
)

# Run the algorithm
algorithm.run()

# Get results
result = algorithm.get_result()

# Print solutions
for solution in result:
    print(f"Variables: {solution.variables}")
    print(f"Objectives: {solution.objectives}")
    print(f"Constraints: {solution.constraints}")
