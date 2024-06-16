import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
from jmetal.operator import PMXCrossover, IntegerPolynomialMutation, CXCrossover, NullCrossover
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator.crossover import IntegerSBXCrossover
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.algorithm.multiobjective.smpso import SMPSO
from jmetal.util.archive import CrowdingDistanceArchive
app = Flask(__name__)
CORS(app)



class RoomAssignmentProblem(IntegerProblem):

    def name(self) -> str:
        return 'Room Assignment Problem'

    def number_of_constraints(self):
        return self.number_of_constraints

    def number_of_objectives(self):
        return self.number_of_objectives

    def number_of_variables(self):
        return self.number_of_variables


    def __init__(self, rooms_df: pd.DataFrame, schedule_df: pd.DataFrame):
        super(RoomAssignmentProblem, self).__init__()
        self.rooms_df = rooms_df
        self.schedule_df = schedule_df

        self.number_of_variables = len(schedule_df)
        #Objetivos:
        #Ter o minimo de sobrelotações
        #Ter o minimo de sobreposições
        #Ter o minimos de aulas com requisitos não cumpridos
        self.number_of_objectives = 3  
        self.number_of_constraints = 0  # No constraints

        self.obj_directions = [self.MINIMIZE, self.MINIMIZE, self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['Overcapacity', 'Overlaps', 'Unmet Requirements']





    def evaluate(self, solution: IntegerSolution):
        overcapacity_count = 0
        overlap_count = 0
        unmet_requirements_count = 0

        room_usage = [[] for _ in range(len(self.rooms_df))]

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            room_index = solution.variables[i]
            room_info = self.rooms_df.iloc[room_index]

            # Check for overcapacity
            class_size = class_info['Inscritos no turno']
            room_capacity = room_info['Capacidade Normal']
            if class_size > room_capacity:
                overcapacity_count += 1

            # Check for overlaps
            start_time = class_info['Início']
            end_time = class_info['Fim']
            for (other_start, other_end) in room_usage[room_index]:
                if not (end_time <= other_start or start_time >= other_end):
                    overlap_count += 1
                    break
            room_usage[room_index].append((start_time, end_time))

            # Check for unmet requirements
            class_requirements = class_info['Características da sala pedida para a aula'].split(', ')
            room_features = [col for col in self.rooms_df.columns[4:] if room_info[col] == 'X']
            for requirement in class_requirements:
                if requirement not in room_features:
                    unmet_requirements_count += 1
                    break

            

        solution.objectives[0] = overcapacity_count
        solution.objectives[1] = overlap_count
        solution.objectives[2] = unmet_requirements_count
        

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
    
@app.route('/optimize', methods=['POST'])
def optimizeSchedule():
    data = request.get_json()
    selected_SingleObjective_Criterium = data['selectedSingleObjectiveCriterium']
    print(selected_SingleObjective_Criterium)
    selected_Otimization_Type = data['selectedOtimizationType']
    print(selected_Otimization_Type)

    ## APAGAR LIXO
    return jsonify({"dummy": "ola"})


    # # Assuming rooms_df and schedule_df are your DataFrames with the necessary data
    # schedule_df = pd.read_csv('HorarioDeExemplo - Copy.csv', delimiter=';', encoding="utf-8")
    # rooms_df = pd.read_csv('CaracterizaçãoDasSalas.csv', delimiter=';', encoding="utf-8")

    # problem = RoomAssignmentProblem(rooms_df, schedule_df)

    # # Define the crossover and mutation operators
    # # crossover_operator = CXCrossover(probability=0.8)
    # crossover_operator = IntegerSBXCrossover(probability=0.8)
    # mutation_operator = IntegerPolynomialMutation(probability=0.2)

    # # Define the algorithm
    # algorithm_NSGAII = NSGAII(
    #     problem=problem,
    #     population_size=10,
    #     offspring_population_size=10,
    #     mutation=mutation_operator,
    #     crossover=crossover_operator,
    #     termination_criterion=StoppingByEvaluations(max_evaluations=200)
    # )

    # # Define the algorithm
    # algorithm_Genetic = GeneticAlgorithm(
    #     problem=problem,
    #     population_size=10,
    #     offspring_population_size=10,
    #     mutation=mutation_operator,
    #     crossover=crossover_operator,
    #     termination_criterion=StoppingByEvaluations(max_evaluations=200)
    # )




    # # progress_bar = ProgressBarObserver(max=200)
    # # algorithm_NSGAII.observable.register(progress_bar)

    # # # Run the algorithm
    # # algorithm_NSGAII.run()

    # # # Get the results
    # # solutions_NSGAII = algorithm_NSGAII.get_result()

    # # # Process the solutions
    # # for solution in solutions_NSGAII:
    # #     print('Solution:', solution.variables)
    # #     print('Objectives:', solution.objectives)

    # # # Assuming 'solution' is the first solution in the obtained solutions from NSGA-II
    # # solution_NSGAII = solutions_NSGAII[0]
    # # room_assignments = solution_NSGAII.variables




    # progress_bar = ProgressBarObserver(max=200)
    # algorithm_Genetic.observable.register(progress_bar)

    # # Run the algorithm
    # algorithm_Genetic.run()

    # # Get the results
    # solutions_Genetic = algorithm_Genetic.get_result()

    # # Process the solutions

    # print('Solution:', solutions_Genetic.variables)
    # print('Objectives:', solutions_Genetic.objectives)

    # # Assuming 'solution' is the first solution in the obtained solutions from NSGA-II
    # solution_Genetic = solutions_Genetic
    # room_assignments = solution_Genetic.variables





    # for i, room_index in enumerate(room_assignments):
    #     room_info = rooms_df.iloc[room_index]
    #     room_name = rooms_df.iloc[room_index]['Nome sala']  # Fetch the room name from rooms_df
    #     capacity = rooms_df.iloc[room_index]['Capacidade Normal']

    #     characteristics = []
    #     for column in rooms_df.columns[4:]:
    #         if column != 'Nº características' and not pd.isna(room_info[column]) and room_info[column] != '':
    #             characteristics.append(column)

    #     schedule_df.at[i, 'Sala da aula'] = room_name  # Replace 'Sala da aula' with the room name
    #     schedule_df.at[i, 'Lotação'] = int(capacity)
    #     schedule_df.at[i, 'Características reais da sala'] = ', '.join(characteristics)

    # schedule_df['Lotação'] = schedule_df['Lotação'].astype(int)

    # # Save the assigned rooms DataFrame to a CSV file
    # schedule_df.to_csv('assigned_rooms.csv', index=False, sep=';', encoding="utf-8")


    # with open('assigned_rooms.csv', 'r', encoding='utf-8') as file:
    #     lines = file.readlines()

    # if lines:
    #     lines[-1] = lines[-1].rstrip('\n')

    # with open('assigned_rooms.csv', 'w', encoding='utf-8') as file:
    #     file.writelines(lines)

if __name__ == '__main__':
    app.run(debug=True)
