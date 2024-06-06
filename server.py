import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.core.solution import FloatSolution
from jmetal.operator import SBXCrossover, PolynomialMutation
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
            count_total_students_overcrowding += int(inscritos - lotacao)
            df.at[index, 'Sobrelotações'] = True
        else:
            df.at[index, 'Sobrelotações'] = False

    criterium_array = {
        'Sobrelotações': count_overcrowding,
        'Alunos a mais (Sobrelotações)': count_total_students_overcrowding
    }

    print("Criterium Overcrowding Array:", criterium_array)  # Debug message

    return df, criterium_array

def criterium_overlapping(df, hour_format):
    # Especificando o formato de data e hora
    df['Início'] = pd.to_datetime(df['Início'], format=hour_format)
    df['Fim'] = pd.to_datetime(df['Fim'], format=hour_format)

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



def criterium_class_requisites(df, class_room_dictionary):
    countRequisitesNotMet = 0
    countNoClassroom = 0

    for index, entry in df.iterrows():
        askedRequisites = entry['Características da sala pedida para a aula']
        roomName = entry['Sala da aula']

        if roomName in class_room_dictionary:
            if askedRequisites not in class_room_dictionary[roomName]:
                countRequisitesNotMet += 1
                df.at[index, 'Requisitos não cumpridos'] = True
                df.at[index, 'Aulas Sem Sala'] = False
            else:
                df.at[index, 'Requisitos não cumpridos'] = False
                df.at[index, 'Aulas Sem Sala'] = False
        elif roomName == "" and askedRequisites != "Não necessita de sala":
            countNoClassroom += 1
            df.at[index, 'Requisitos não cumpridos'] = True
            df.at[index, 'Aulas Sem Sala'] = True
        else:
            df.at[index, 'Requisitos não cumpridos'] = False
            df.at[index, 'Aulas Sem Sala'] = False

    criterium_array = {
        'Requisitos não cumpridos': countRequisitesNotMet,
        'Aulas Sem Sala': countNoClassroom
    }

    print(criterium_array)

    return df, criterium_array

def convert_js_format_to_python(js_format):
    format_map = {
        'HH:mm:ss': '%H:%M:%S',
        'hh:mm:ss A': '%I:%M:%S %p',
        'HH:mm': '%H:%M',
        'hh:mm A': '%I:%M %p',

        'YYYY-MM-DD': '%Y-%m-%d',
        'DD/MM/YYYY': '%d/%m/%Y',
        'MM/DD/YYYY': '%m/%d/%Y',
        'YYYY/MM/DD': '%Y/%m/%d'
    }

    return format_map.get(js_format, js_format)

import math



def evaluate_dynamic_formula_criteria(df, expressions):
    criteria_results = {}
    
    for expression in expressions:
        expression = expression.strip()  # Remove any leading or trailing whitespace
        found_column_names = extract_column_names_from_expression(expression, df.columns)
        true_count = 0  # Counter for the number of true rows
        error_counter = 0
        
        for index, row in df.iterrows():
            error_occurred = False
            row_specific_expression = expression
            
            for column_name in found_column_names:
                value = row[column_name]
                row_specific_expression = row_specific_expression.replace(column_name, str(value))
            
            try:
                result = eval(row_specific_expression)
                if result:
                    true_count += 1  # Increment the counter if the expression is true for this row
                    df.at[index, expression] = True
                else:
                    df.at[index, expression] = False
            except Exception as error:
                print(f"Error evaluating expression for row {index}: {error}")
                error_occurred = True
                error_counter += 1
                df.at[index, expression] = False
        
        if error_counter == len(df):
            print(f"Ocorreu um erro na expressão '{expression}' e por isso não foram adicionados novos critérios, por favor, corrija a fórmula!")
        
        criteria_results[expression] = true_count
    
    print(criteria_results)
    
    return df, criteria_results

# Example usage:
# Assuming df is your DataFrame and 'expressions' is a string of comma-separated expressions
# df, results = evaluate_dynamic_formula_criteria(df, 'expression1, expression2, expression3')


def extract_column_names_from_expression(expression, all_column_names):
    found_column_names = []
    for column_name in all_column_names:
        if column_name in expression:
            found_column_names.append(column_name)
    return found_column_names



def check_for_exact_word_match(expression, input_word):
    regex_string = fr'\b{re.escape(input_word)}\b(?![\w-])'
    regex = re.compile(regex_string)
    return bool(regex.search(expression))

def evaluate_dynamic_text_criteria(selected_schedule_data_df, criteria_list):
    results = {}
    
    for column, input_text in criteria_list:
        input_parsed = input_text.replace('.', ' ')  # Problema com o Tabulator
        field_name = f"{column}={input_parsed}"
        true_count = 0
        
        for index, row in selected_schedule_data_df.iterrows():
            if check_for_exact_word_match(row[column], input_text):
                selected_schedule_data_df.at[index, field_name] = True
                true_count += 1
            else:
                selected_schedule_data_df.at[index, field_name] = False
        
        results[field_name] = true_count

    print(results)

    return selected_schedule_data_df, results


def process_message():
    data = request.get_json()
    selected_schedule_data = data['selectedScheduleData']
    class_room_dictionary = data['classRoomDictionary']
    hour_format = data['hourFormat']
    date_format = data['dateFormat']
    formula_criterium_list = data['formulaCriteriumList']
    print(formula_criterium_list)
    text_criterium_list = data['textCriteriumList']
    print(text_criterium_list)

    hour_format = convert_js_format_to_python(hour_format)
    date_format = convert_js_format_to_python(date_format)


    selected_schedule_data_df = pd.DataFrame(selected_schedule_data)

    
    show_selected_schedule_data_df = selected_schedule_data_df.head(2)

    #print(show_selected_schedule_data_df)
    
    selected_schedule_data_df, overcrowding_criterium = criterium_overcrowding(selected_schedule_data_df)
    # df, overlapping_criterium = criterium_overlapping(selected_schedule_data_df, hour_format)
    # selected_schedule_data_df, class_requisites_criterium = criterium_class_requisites(selected_schedule_data_df, class_room_dictionary)
    
    # expression = "Lotação - Inscritos no turno > 20"
    # dynamic_evaluated_df, expression_criterium = evaluate_dynamic_formula_criterium(selected_schedule_data_df, expression)

    # criteriums = {**overcrowding_criterium, **overlapping_criterium, **class_requisites_criterium} 
    # criteriums = {**overcrowding_criterium, **expression_criterium}

    criteriums = {**overcrowding_criterium}
    # print("Criteriums:", criteriums)  # Debug message

    return jsonify({"criteriums": criteriums})

    df, formulaCriteriaResults = evaluate_dynamic_formula_criteria(selected_schedule_data_df, formula_criterium_list)

    print(formulaCriteriaResults)

    selected_schedule_data_df, textCriteriaResults = evaluate_dynamic_text_criteria(selected_schedule_data_df, text_criterium_list)
    print(textCriteriaResults)

class TimetableProblem(Problem):
    def __init__(self, df: pd.DataFrame, class_room_dictionary: dict):
        super(TimetableProblem, self).__init__()
        self.df = df
        self.class_room_dictionary = class_room_dictionary
        self._number_of_variables = df.shape[0] * df.shape[1]
        self._number_of_objectives = 4
        self._number_of_constraints = 0
        self.lower_bound = [0.0] * self._number_of_variables
        self.upper_bound = [1.0] * self._number_of_variables

    @property
    def number_of_variables(self):
        return self._number_of_variables

    @property
    def number_of_objectives(self):
        return self._number_of_objectives

    @property
    def number_of_constraints(self):
        return self._number_of_constraints

    @property
    def name(self):
        return 'TimetableProblem'

    def evaluate(self, solution: FloatSolution) -> FloatSolution:
        # Calcular critérios
        df, overcrowding_criterium = criterium_overcrowding(self.df)
        df, overlapping_criterium = criterium_overlapping(self.df, "%H:%M:%S")
        df, class_requisites_criterium = criterium_class_requisites(self.df, self.class_room_dictionary)
        
        # Funções objetivo
        objectives = [
            overcrowding_criterium['Alunos a mais (Sobrelotações)'],
            overlapping_criterium['Sobreposições'],
            class_requisites_criterium['Requisitos não cumpridos'],
            class_requisites_criterium['Aulas Sem Sala']
        ]
        
        solution.objectives = objectives[:self.number_of_objectives]  # Adjust the objectives based on the defined number
        return solution

    def create_solution(self) -> FloatSolution:
        new_solution = FloatSolution(self.lower_bound, self.upper_bound, self.number_of_objectives)
    
        # Assuming the DataFrame represents a timetable where each row is a class/session
        num_rows, num_cols = self.df.shape
        
        # Initializing a list to hold the solution variables
        variables = []
        
        for i in range(num_rows):
            row_variables = []
            for j in range(num_cols):
                # Generate variables based on some logic, here using uniform distribution
                # This can be refined to better reflect the problem constraints
                if self.df.columns[j] in ['Inscritos no turno', 'Lotação']:
                    value = np.random.randint(0, 100)  # Simulate enrollment and capacity between 0 and 100
                elif self.df.columns[j] in ['Início', 'Fim']:
                    # Simulate time as a fraction of a day (0 to 1)
                    value = np.random.uniform(0.0, 1.0)
                else:
                    value = np.random.uniform(0.0, 1.0)  # Generic value for other columns
                row_variables.append(value)
            variables.extend(row_variables)
        
        # Assigning the generated variables to the solution
        new_solution.variables = variables
        
        return new_solution

@app.route('/process', methods=['POST'])
def optimize():
    data = request.get_json()
    selected_schedule_data = data['selectedScheduleData']
    class_room_dictionary = data['classRoomDictionary']
    hour_format = data['hourFormat']
    date_format = data['dateFormat']

    hour_format = convert_js_format_to_python(hour_format)
    date_format = convert_js_format_to_python(date_format)


    df = pd.DataFrame(selected_schedule_data)
   
    problem = TimetableProblem(df, class_room_dictionary)

    algorithm = NSGAII(
        problem=problem,
        population_size=10,
        offspring_population_size=10,
        mutation=PolynomialMutation(probability=0.1, distribution_index=20),
        crossover=SBXCrossover(probability=0.9, distribution_index=20),
        termination_criterion=StoppingByEvaluations(max_evaluations=100)
    )

    algorithm.run()

    result = algorithm.get_result()

    """ for solution in result:
        print(f'Solution: {solution.variables}')
        print(f'Objectives: {solution.objectives}') """

    best_solution = result[0].variables
    optimized_timetable = pd.DataFrame(
    [best_solution[i:i+df.shape[1]] for i in range(0, len(best_solution), df.shape[1])],
    columns=df.columns
    )
    print(optimized_timetable)

if __name__ == '__main__':
    app.run(debug=True)