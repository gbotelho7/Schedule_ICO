from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.operator import BinaryTournamentSelection, SPXCrossover, BitFlipMutation
from jmetal.util.termination_criterion import StoppingByEvaluations
from jmetal.core.problem import Problem

app = Flask(__name__)
CORS(app)


def criterium_overcrowding(df):
    count_overcrowding = 0
    count_total_students_overcrowding = 0

    # Convertendo as colunas relevantes para números
    df['Lotação'] = pd.to_numeric(df['Lotação'], errors='coerce')
    df['Inscritos no turno'] = pd.to_numeric(df['Inscritos no turno'], errors='coerce')

    # Verificando se há valores NaN e substituindo por 0 (ou outra lógica desejada)
    df['Lotação'] = df['Lotação'].fillna(0)
    df['Inscritos no turno'] = df['Inscritos no turno'].fillna(0)

    for index, row in df.iterrows():
        lotacao = row['Lotação']
        inscritos = row['Inscritos no turno']

        if inscritos > lotacao:
            count_overcrowding += 1
            count_total_students_overcrowding += inscritos - lotacao
            df.at[index, 'Sobrelotações'] = True
        else:
            df.at[index, 'Sobrelotações'] = False

    criterium_array = {
        'Sobrelotações': count_overcrowding,
        'Alunos a mais (Sobrelotações)': count_total_students_overcrowding
    }

    print("Criterium Overcrowding Array:", criterium_array)  # Debug message

    return df, criterium_array

def criterium_overlapping(df):
    # Especificando o formato de data e hora
    df['Início'] = pd.to_datetime(df['Início'], format='%H:%M:%S')
    df['Fim'] = pd.to_datetime(df['Fim'], format='%H:%M:%S')

    classes_by_date = df.groupby('Dia')
    count_overlapping = 0

    for date, classes_for_date in classes_by_date:
        classes_for_date = classes_for_date.sort_values('Início').reset_index(drop=True)
        for i in range(len(classes_for_date) - 1):
            is_true = False
            for j in range(i + 1, len(classes_for_date)):
                if (classes_for_date.at[i, 'Início'] < classes_for_date.at[j, 'Fim'] and classes_for_date.at[i, 'Fim'] > classes_for_date.at[j, 'Início']) or \
                   (classes_for_date.at[j, 'Início'] < classes_for_date.at[i, 'Fim'] and classes_for_date.at[j, 'Fim'] > classes_for_date.at[i, 'Início']):
                    count_overlapping += 1
                    is_true = True
            if is_true:
                df.at[classes_for_date.index[i], 'Sobreposições'] = True
            else:
                df.at[classes_for_date.index[i], 'Sobreposições'] = False

    criterium_array = {
        'Sobreposições': count_overlapping
    }

    print("Criterium Overlapping Array:", criterium_array)  # Debug message

    return df, criterium_array 



def criterium_class_requisites(results, class_room_dictionary):
    countRequisitesNotMet = 0
    countNoClassroom = 0

    for index, entry in results.iterrows():
        askedRequisites = entry['Características da sala pedida para a aula']
        roomName = entry['Sala da aula']

        if roomName in class_room_dictionary:
            if askedRequisites not in class_room_dictionary[roomName]:
                countRequisitesNotMet += 1
                results.at[index, 'Requisitos não cumpridos'] = True
                results.at[index, 'Aulas Sem Sala'] = False
            else:
                results.at[index, 'Requisitos não cumpridos'] = False
                results.at[index, 'Aulas Sem Sala'] = False
        elif roomName == "" and askedRequisites != "Não necessita de sala":
            countNoClassroom += 1
            results.at[index, 'Requisitos não cumpridos'] = True
            results.at[index, 'Aulas Sem Sala'] = True
        else:
            results.at[index, 'Requisitos não cumpridos'] = False
            results.at[index, 'Aulas Sem Sala'] = False

    criterium_array = {
        'Requisitos não cumpridos': countRequisitesNotMet,
        'Aulas Sem Sala': countNoClassroom
    }

    print(criterium_array)

    return results, criterium_array



""" @app.route('/process', methods=['POST'])
def process_message():
    data = request.get_json()
    selected_schedule_data = data['selectedScheduleData']
    class_room_dictionary = data['classRoomDictionary']


    selected_schedule_data_df = pd.DataFrame(selected_schedule_data)
    
    
    
    first_row = selected_schedule_data_df.head(1).to_dict(orient='records')
    
    selected_schedule_data_df, overcrowding_criterium = criterium_overcrowding(selected_schedule_data_df)
    df, overlapping_criterium = criterium_overlapping(selected_schedule_data_df)
    selected_schedule_data_df, class_requisites_criterium = criterium_class_requisites(selected_schedule_data_df, class_room_dictionary)


    
    criteriums = {**overcrowding_criterium, **overlapping_criterium, **class_requisites_criterium} 


    print("Criteriums:", criteriums)  # Debug message

    return jsonify({"primeira_linha": first_row, "criteriums": criteriums}) """

if __name__ == '__main__':
    app.run(debug=True)



class TimetableProblem(Problem):
    def __init__(self, number_of_variables: int, data):
        super(TimetableProblem, self).__init__(number_of_variables=number_of_variables)
        self.data = data
        self.number_of_objectives = 1
        self.number_of_constraints = 0
        self.obj_directions = [self.MINIMIZE] * self.number_of_objectives
        self.obj_labels = ['schedule_quality']
        self.lower_bound = [0] * self.number_of_variables
        self.upper_bound = [1] * self.number_of_variables

    def evaluate(self, solution: BinarySolution) -> BinarySolution:
        conflicts = 0
        room_utilization = 0

        # Custom evaluation logic
        timetable = self.decode_solution(solution)
        
        for timeslot in timetable:
            classes_in_slot = timetable[timeslot]
            teachers = set()
            rooms = set()
            for cls in classes_in_slot:
                if cls['teacher'] in teachers:
                    conflicts += 1
                else:
                    teachers.add(cls['teacher'])
                if cls['room'] in rooms:
                    conflicts += 1
                else:
                    rooms.add(cls['room'])

            room_utilization += len(rooms) / len(self.get_all_rooms())

        solution.objectives[0] = conflicts - room_utilization  # Combine conflicts and room utilization
        return solution
    
    def create_solution(self) -> BinarySolution:
        new_solution = BinarySolution(number_of_variables=self.number_of_variables, number_of_objectives=self.number_of_objectives)
        new_solution.variables = [np.random.randint(2) for _ in range(self.number_of_variables)]
        return new_solution
    def decode_solution(self, solution: BinarySolution):
        # Decoding logic to convert the binary solution to a readable timetable format
        timetable = {}
        for idx, val in enumerate(solution.variables):
            if val == 1:
                timeslot = self.data[idx]['timeslot']
                if timeslot not in timetable:
                    timetable[timeslot] = []
                timetable[timeslot].append(self.data[idx])
        return timetable

    def get_all_rooms(self):
        # Example function to get all available rooms
        rooms = set()
        for entry in self.data:
            rooms.add(entry['room'])
        return rooms
    
    def get_name(self) -> str:
        return 'TimetableProblem'

@app.route('/process', methods=['POST'])
def optimize_timetable():
    data = request.json.get()
    number_of_variables = len(data)  # Adjust this based on your actual data structure

    # Define the problem
    problem = TimetableProblem(number_of_variables=number_of_variables, data=data)

    # Configure the algorithm
    algorithm = NSGAII(
        problem=problem,
        population_size=100,
        offspring_population_size=100,
        mutation=BitFlipMutation(probability=0.1),
        crossover=SPXCrossover(probability=0.9),
        selection=BinaryTournamentSelection(),
        termination_criterion=StoppingByEvaluations(max_evaluations=1000)
    )

    # Run the algorithm
    algorithm.run()

    # Get the result and return the best 10 solutions
    result = algorithm.get_result()
    best_solutions = sorted(result, key=lambda s: s.objectives[0])[:10]

    response = []
    for solution in best_solutions:
        response.append({
            'variables': solution.variables,
            'objective': solution.objectives[0]
        })

    print(response)
    return jsonify(response)
