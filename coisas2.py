import random
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from jmetal.core.problem import IntegerProblem
from jmetal.core.solution import IntegerSolution
from jmetal.operator import IntegerPolynomialMutation
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator.crossover import IntegerSBXCrossover
from jmetal.util.observer import ProgressBarObserver
from jmetal.util.termination_criterion import StoppingByEvaluations

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

        # if selected_Otimization_Type == "multi":
        self.number_of_objectives = 2
        self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
        self.obj_labels = ['Overcapacity', 'Unmet Requirements']

        # else:
        #     self.number_of_objectives = 1
        #     self.obj_directions = [self.MINIMIZE]
        #     self.obj_labels = [selected_SingleObjective_Criterium]

        self.number_of_constraints = 0  # No constraints

    # def __init__(self, rooms_df: pd.DataFrame, schedule_df: pd.DataFrame, ):
    #     super(RoomAssignmentProblem, self).__init__()
    #     self.rooms_df = rooms_df
    #     self.schedule_df = schedule_df

    #     self.number_of_variables = len(schedule_df)

    #     self.number_of_objectives = 3
    #     self.obj_directions = [self.MINIMIZE, self.MINIMIZE, self.MINIMIZE]
    #     self.obj_labels = ['Overcapacity', 'Overlaps', 'Unmet Requirements']


    #     self.number_of_constraints = 0  # No constraints





    def evaluate(self, solution: IntegerSolution):
        overcapacity_count = 0
        unmet_requirements_count = 0

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            class_requirements = str(class_info['Características da sala pedida para a aula']).split(', ')
            room_index = solution.variables[i]
            room_info = self.rooms_df.iloc[room_index]

            class_size = class_info['Inscritos no turno']
            room_capacity = room_info['Capacidade Normal']
            if class_size > room_capacity:
                overcapacity_count += 1
                
            if room_index != -1:
                room_info = self.rooms_df.iloc[room_index]
                room_features = [col for col in self.rooms_df.columns[5:] if room_info[col] == 'X']
                for requirement in class_requirements:
                    if requirement == "Não necessita de sala":
                        continue
                    if not any(requirement in feature for feature in room_features):                    
                        if (requirement == "Sala/anfiteatro aulas" and 
                            ("Sala de Aulas normal" in room_features or "Anfiteatro aulas" in room_features)):
                            unmet_requirements_count += 0
                        elif (requirement == "Lab ISTA" and 
                                any(feature for feature in room_features if "Laboratório" in feature and feature != "Laboratório de Informática")):
                            unmet_requirements_count += 0
                        elif (requirement == "Anfiteatro aulas" and "Sala/anfiteatro aulas" in room_features):
                            unmet_requirements_count += 0
                        else:
                            unmet_requirements_count += 1
                            break
            else:
                if class_requirements != "Não necessita de sala":
                    unmet_requirements_count += 1


        solution.objectives[0] = overcapacity_count
        solution.objectives[1] = unmet_requirements_count
         
    def create_solution(self) -> IntegerSolution:
        solution = IntegerSolution(
            number_of_objectives=self.number_of_objectives,
            number_of_constraints=self.number_of_constraints,
            lower_bound=[-1] * self.number_of_variables,  # Lower bound for each variable
            upper_bound=[len(self.rooms_df) - 1] * self.number_of_variables  # Upper bound for each variable
        )

        # Ordenar salas por capacidade para tentativa de alocação mais adequada
        sorted_rooms = self.rooms_df.sort_values(by='Capacidade Normal').reset_index()

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            class_size = class_info['Inscritos no turno']
            class_requirements = str(class_info['Características da sala pedida para a aula']).split(', ')

            if 'Não necessita de sala' not in class_requirements:
                # Tentar encontrar uma sala adequada
                assigned = False
                for j, room_info in sorted_rooms.iterrows():
                    room_capacity = room_info['Capacidade Normal']
                    if class_size <= room_capacity:
                        room_features = [col for col in self.rooms_df.columns[5:] if room_info[col] == 'X']
                        if all(req in room_features for req in class_requirements):
                            solution.variables[i] = room_info['index']
                            assigned = True
                            break
                        else:
                            for requirement in class_requirements:
                                if requirement == "Não necessita de sala":
                                    continue
                                if not any(requirement in feature for feature in room_features):
                                    if (requirement == "Sala/anfiteatro aulas" and ("Sala de Aulas normal" in room_features or "Anfiteatro aulas" in room_features)):
                                        solution.variables[i] = room_info['index']
                                        assigned = True
                                        break
                                    elif (requirement == "Lab ISTA" and any(feature for feature in room_features if "Laboratório" in feature and feature != "Laboratório de Informática")):
                                        solution.variables[i] = room_info['index']
                                        assigned = True
                                        break
                                    elif (requirement == "Anfiteatro aulas" and "Sala/anfiteatro aulas" in room_features):
                                        solution.variables[i] = room_info['index']
                                        assigned = True
                                        break
                                    else:
                                        #print("entrei")
                                        #unmet_requirements_count += 1
                                        break
                # Se não encontrar uma sala ideal, atribuir aleatoriamente dentro dos limites
                if not assigned:
                    solution.variables[i] = random.randint(0, len(self.rooms_df) - 1)
            else:
                solution.variables[i] = -1

        return solution
    
    


# selected_SingleObjective_Criterium = "sobreposições"
# selected_Otimization_Type = "single"c

    
@app.route('/optimize', methods=['POST'])
def optimizeSchedule():
    data = request.get_json()
    schedule_File_Name = data['scheduleFileName']
    rooms_Chars_FileName = data['roomsCharsFileName']
    selected_SingleObjective_Criterium = data['selectedSingleObjectiveCriterium']
    selected_Otimization_Type = data['selectedOtimizationType']
    filename_otimization = data['otimizedSolutionFileName']
    optimize( schedule_File_Name, rooms_Chars_FileName, selected_Otimization_Type, selected_SingleObjective_Criterium, filename_otimization)

    ## APAGAR LIXO
    return jsonify({"dummy": "ola"})



def optimize( schedule_File_Name, rooms_Chars_FileName, selected_Otimization_Type, selected_SingleObjective_Criterium="Null", filename_otimization="Null" ):

    rooms_df = pd.read_csv(rooms_Chars_FileName, delimiter=';', encoding="utf-8")
    schedule_df = pd.read_csv(schedule_File_Name, delimiter=';', encoding="utf-8")
    print(type(schedule_df))
    selected_Otimization_Type = selected_Otimization_Type
    selected_SingleObjective_Criterium = selected_SingleObjective_Criterium


    # Assuming rooms_df and schedule_df are your DataFrames with the necessary data
    # schedule_df = pd.read_csv('HorarioDeExemplo.csv', delimiter=';', encoding="utf-8")
    # rooms_df = pd.read_csv('CaracterizaçãoDasSalas.csv', delimiter=';', encoding="utf-8")

    problem = RoomAssignmentProblem(rooms_df, schedule_df)

    # Define the crossover and mutation operators
    # crossover_operator = CXCrossover(probability=0.8)
    crossover_operator = IntegerSBXCrossover(probability=0.8)
    mutation_operator = IntegerPolynomialMutation(probability=0.2)



    # Define the algorithm
    algorithm_NSGAII = NSGAII(
        problem=problem,
        population_size=10,
        offspring_population_size=10,
        mutation=mutation_operator,
        crossover=crossover_operator,
        termination_criterion=StoppingByEvaluations(max_evaluations=200)
    )

    # Define the algorithm
    algorithm_Genetic = GeneticAlgorithm(
        problem=problem,
        population_size=10,
        offspring_population_size=10,
        mutation=mutation_operator,
        crossover=crossover_operator,
        termination_criterion=StoppingByEvaluations(max_evaluations=200)
    )




    progress_bar = ProgressBarObserver(max=200)
    algorithm_NSGAII.observable.register(progress_bar)

    # Run the algorithm
    algorithm_NSGAII.run()

    # Get the results
    solutions_NSGAII = algorithm_NSGAII.get_result()

    # Process the solutions
    for solution in solutions_NSGAII:
        # print('Solution:', solution.variables)
        print('Objectives:', solution.objectives)



    # Assuming 'solution' is the first solution in the obtained solutions from NSGA-II
    solution_NSGAII = solutions_NSGAII[0]
    room_assignments = solution_NSGAII.variables

    # print(solution_NSGAII.objectives)
    # print(solution_NSGAII.variables)






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




    for i, room_index in enumerate(room_assignments):
        if room_index == -1:

            schedule_df.at[i, 'Sala da aula'] = ""             
            schedule_df.at[i, 'Lotação'] = ""
            schedule_df.at[i, 'Características reais da sala'] = ""
        else:
            room_info = rooms_df.iloc[room_index]
            room_name = rooms_df.iloc[room_index]['Nome sala']  # Fetch the room name from rooms_df
            capacity = rooms_df.iloc[room_index]['Capacidade Normal']

            characteristics = []
            for column in rooms_df.columns[4:]:
                if column != 'Nº características' and not pd.isna(room_info[column]) and room_info[column] != '':
                    characteristics.append(column)

                schedule_df.at[i, 'Sala da aula'] = room_name  # Replace 'Sala da aula' with the room name

                
            schedule_df.at[i, 'Lotação'] = int(capacity)
            schedule_df.at[i, 'Características reais da sala'] = ', '.join(characteristics)
            schedule_df.at[i, 'Lotação'] = int(schedule_df.at[i, 'Lotação'])



    # Save the assigned rooms DataFrame to a CSV file
    schedule_df.to_csv(filename_otimization, index=False, sep=';', encoding="utf-8")


    with open(filename_otimization, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    if lines:
        lines[-1] = lines[-1].rstrip('\n')

    with open(filename_otimization, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == '__main__':
    app.run(debug=True)