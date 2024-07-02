import os
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from matplotlib import pyplot as plt
import numpy as np
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
    
    def selected_Otimization_Type(self):
        return self.selected_Otimization_Type
    
    def selected_SingleObjective_Criterium(self):
        return self.selected_SingleObjective_Criterium


    def __init__(self, rooms_df: pd.DataFrame, schedule_df: pd.DataFrame, selected_Otimization_Type: str, selected_SingleObjective_Criterium: str):
        super(RoomAssignmentProblem, self).__init__()
        self.rooms_df = rooms_df
        self.schedule_df = schedule_df

        self.selected_Otimization_Type = selected_Otimization_Type
        self.selected_SingleObjective_Criterium = selected_SingleObjective_Criterium

        self.number_of_variables = len(schedule_df)

        if selected_Otimization_Type == "multi":
            self.number_of_objectives = 2
            self.obj_directions = [self.MINIMIZE, self.MINIMIZE]
            self.obj_labels = ['Overcapacity', 'Unmet Requirements']

        else:
            self.number_of_objectives = 1
            self.obj_directions = [self.MINIMIZE]
            self.obj_labels = [selected_SingleObjective_Criterium]

        self.number_of_constraints = 0  # No constraints

    def evaluate(self, solution: IntegerSolution):
        overcapacity_count = 0
        unmet_requirements_count = 0

        for i in range(self.number_of_variables):
            class_info = self.schedule_df.iloc[i]
            class_requirements = str(class_info['Características da sala pedida para a aula']).split(', ')
            room_index = solution.variables[i]
            room_info = self.rooms_df.iloc[room_index]

            
            if(self.selected_Otimization_Type == "multi" or self.selected_SingleObjective_Criterium == "Sobrelotações"):
                class_size = class_info['Inscritos no turno']
                room_capacity = room_info['Capacidade Normal']
                if class_size > room_capacity:
                    overcapacity_count += 1

            if(self.selected_Otimization_Type == "multi" or self.selected_SingleObjective_Criterium== "Requisitos não cumpridos"):         
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

        if(self.selected_Otimization_Type == "multi"):
            solution.objectives[0] = overcapacity_count
            solution.objectives[1] = unmet_requirements_count
        elif self.selected_SingleObjective_Criterium == "Sobrelotações":
            solution.objectives[0] = overcapacity_count
        else:
            solution.objectives[0] = unmet_requirements_count
         
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


def pareto_frontier(obj1, obj2, maxX=True, maxY=True):
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

@app.route('/optimize', methods=['POST'])
def optimizeSchedule():
    data = request.get_json()
    schedule_File_Name = data['scheduleFileName']
    rooms_Chars_FileName = data['roomsCharsFileName']
    selected_SingleObjective_Criterium = data['selectedSingleObjectiveCriterium']
    selected_Otimization_Type = data['selectedOtimizationType']
    filename_otimization = data['otimizedSolutionFileName']
    optimize( schedule_File_Name, rooms_Chars_FileName, selected_Otimization_Type, filename_otimization,selected_SingleObjective_Criterium)

    return jsonify({"status": "Otimização concluída"})

def optimize( schedule_File_Name, rooms_Chars_FileName, selected_Otimization_Type, filename_otimization,selected_SingleObjective_Criterium="Null" ):
    print(schedule_File_Name)
    rooms_df = pd.read_csv(rooms_Chars_FileName, delimiter=';', encoding="utf-8")
    schedule_df = pd.read_csv(schedule_File_Name, delimiter=';', encoding="utf-8")
    selected_Otimization_Type = selected_Otimization_Type
    selected_SingleObjective_Criterium = selected_SingleObjective_Criterium

    problem = RoomAssignmentProblem(rooms_df, schedule_df,selected_Otimization_Type, selected_SingleObjective_Criterium)



    crossover_operator = IntegerSBXCrossover(probability=0.8)
    mutation_operator = IntegerPolynomialMutation(probability=0.2)

    if selected_Otimization_Type == "multi":

        algorithm = NSGAII(
            problem=problem,
            population_size=10,
            offspring_population_size=10,
            mutation=mutation_operator,
            crossover=crossover_operator,
            termination_criterion=StoppingByEvaluations(max_evaluations=200)
        )
    else:

        algorithm = GeneticAlgorithm(
            problem=problem,
            population_size=10,
            offspring_population_size=10,
            mutation=mutation_operator,
            crossover=crossover_operator,
            termination_criterion=StoppingByEvaluations(max_evaluations=200)
        )

    progress_bar = ProgressBarObserver(max=200)
    algorithm.observable.register(progress_bar)


    algorithm.run()

    # Get the results
    solutions = algorithm.get_result()

    if selected_Otimization_Type == "multi":

        objectiveSobrelotacoes = [solution.objectives[0] for solution in solutions]
        objectiveRequisitos = [solution.objectives[1] for solution in solutions]
    else:
        solution = solutions
        if selected_SingleObjective_Criterium == "Sobrelotações":
            objectiveSobrelotacoes = [solution.objectives[0]]
            objectiveRequisitos = []
        else:
            objectiveSobrelotacoes = []
            objectiveRequisitos = [solution.objectives[0]]

    output_dir = filename_otimization + '_graphs'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if selected_Otimization_Type == "multi":
        plt.figure(figsize=(12, 8))
        plt.scatter(objectiveSobrelotacoes, objectiveRequisitos, color='blue')
        plt.title('Multi-objective Optimization Results', fontsize=16)
        plt.xlabel('Sobrelotações', fontsize=14)
        plt.ylabel('Requisitos Não Cumpridos', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'scatter_plot.png'))
        plt.show()

        pareto = pareto_frontier(objectiveSobrelotacoes, objectiveRequisitos, maxX=False, maxY=True)
        plt.figure(figsize=(12, 8))
        plt.scatter(objectiveSobrelotacoes, objectiveRequisitos, color='blue', label='Solutions')
        plt.plot(pareto[:, 0], pareto[:, 1], color='red', linestyle='--', marker='o', label='Pareto Frontier')
        plt.title('Pareto Frontier', fontsize=16)
        plt.xlabel('Sobrelotações', fontsize=14)
        plt.ylabel('Requisitos Não Cumpridos', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'pareto_frontier.png'))
        plt.show()

        plt.figure(figsize=(12, 8))
        plt.boxplot(objectiveSobrelotacoes)
        plt.title('Boxplot of Sobrelotações', fontsize=16)
        plt.ylabel('Value', fontsize=14)
        plt.xticks([1], ['Sobrelotações'], fontsize=12)
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'boxplot_sobrelotacoes.png'))
        plt.show()

        plt.figure(figsize=(12, 8))
        plt.boxplot(objectiveRequisitos)
        plt.title('Boxplot of Requisitos Não Cumpridos', fontsize=16)
        plt.ylabel('Value', fontsize=14)
        plt.xticks([1], ['Requisitos Não Cumpridos'], fontsize=12)
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'boxplot_requisitos.png'))
        plt.show()

        plt.figure(figsize=(12, 8))
        plt.hist(objectiveSobrelotacoes, bins=10, color='blue', alpha=0.7)
        plt.title('Histogram of Sobrelotações', fontsize=16)
        plt.xlabel('Sobrelotações', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'histogram_sobrelotacoes.png'))
        plt.show()

        plt.figure(figsize=(12, 8))
        plt.hist(objectiveRequisitos, bins=10, color='blue', alpha=0.7)
        plt.title('Histogram of Requisitos Não Cumpridos', fontsize=16)
        plt.xlabel('Requisitos Não Cumpridos', fontsize=14)
        plt.ylabel('Frequency', fontsize=14)
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'histogram_requisitos.png'))
        plt.show()

    for i, room_index in enumerate(solutions.variables if selected_Otimization_Type == "single" else solutions[0].variables):
        if room_index == -1:
            schedule_df.at[i, 'Sala da aula'] = ""
            schedule_df.at[i, 'Lotação'] = ""
            schedule_df.at[i, 'Características reais da sala'] = ""
        else:
            room_info = rooms_df.iloc[room_index]
            room_name = rooms_df.iloc[room_index]['Nome sala']
            capacity = rooms_df.iloc[room_index]['Capacidade Normal']
            characteristics = [column for column in rooms_df.columns[4:] if
                               column != 'Nº características' and not pd.isna(room_info[column]) and room_info[
                                   column] != '']
            schedule_df.at[i, 'Sala da aula'] = room_name
            schedule_df.at[i, 'Lotação'] = int(capacity)
            schedule_df.at[i, 'Características reais da sala'] = ', '.join(characteristics)




    schedule_df.to_csv(filename_otimization, index=False, sep=';', encoding="utf-8")


    with open(filename_otimization, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    if lines:
        lines[-1] = lines[-1].rstrip('\n')
    with open(filename_otimization, 'w', encoding='utf-8') as file:
        file.writelines(lines)

if __name__ == '__main__':
    app.run(debug=True)