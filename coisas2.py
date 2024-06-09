import random
import pandas as pd
from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
from jmetal.operator import PMXCrossover, IntegerPolynomialMutation, CXCrossover
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.termination_criterion import StoppingByEvaluations


class RoomAssignmentProblem(IntegerProblem):
    def name(self) -> str:
        return 'Room Assignment Problem'

    def number_of_constraints(self) -> int:
        return self.number_of_constraints

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

    def evaluate(self, solution: IntegerSolution):
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

    def create_solution(self) -> IntegerSolution:
        solution = IntegerSolution(
            number_of_objectives=self.number_of_objectives,
            number_of_constraints=self.number_of_constraints,
            lower_bound=[0] * self.number_of_variables,  # Lower bound for each variable
            upper_bound=[len(self.rooms_df) - 1] * self.number_of_variables  # Upper bound for each variable
        )

        # Random initialization within bounds
        for i in range(self.number_of_variables):
            solution.variables[i] = random.randint(0, len(self.rooms_df) - 1)

        return solution


# Assuming rooms_df and schedule_df are your DataFrames with the necessary data
schedule_df = pd.read_csv('HorarioDeExemplo - Copy (2).csv', delimiter=';', encoding="utf-8")
rooms_df = pd.read_csv('CaracterizaçãoDasSalas.csv', delimiter=';', encoding="utf-8")

problem = RoomAssignmentProblem(rooms_df, schedule_df)

# Define the crossover and mutation operators
crossover_operator = CXCrossover(probability=0.8)
mutation_operator = IntegerPolynomialMutation(probability=0.2)

# Define the algorithm
algorithm = GeneticAlgorithm(
    problem=problem,
    population_size=10,
    offspring_population_size=10,
    mutation=mutation_operator,
    crossover=crossover_operator,
    termination_criterion=StoppingByEvaluations(max_evaluations=10)
)

progress_bar = ProgressBarObserver(max=10)
algorithm.observable.register(progress_bar)

# Run the algorithm
algorithm.run()

# Get the results
solution = algorithm.get_result()

print('Solution:', solution.variables)
print('Objectives:', solution.objectives)

# Assuming 'solution' is the obtained solution from the genetic algorithm
room_assignments = solution.variables

for i, room_index in enumerate(room_assignments):
    room_info = rooms_df.iloc[room_index]
    room_name = rooms_df.iloc[room_index]['Nome sala']  # Fetch the room name from rooms_df
    capacity = rooms_df.iloc[room_index]['Capacidade Normal']

    characteristics = []
    for column in rooms_df.columns[4:]:
        if column != 'Nº características' and not pd.isna(room_info[column]) and room_info[column] != '':
            characteristics.append(column)

    schedule_df.at[i, 'Sala'] = room_name  # Replace 'Sala da aula' with the room name
    schedule_df.at[i, 'Lotação'] = capacity
    schedule_df.at[i, 'Características reais da sala'] = ', '.join(characteristics)

# Save the assigned rooms DataFrame to a CSV file
schedule_df.to_csv('assigned_rooms.csv', index=False, sep=';', encoding="utf-8")
