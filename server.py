from flask import Flask, logging, request, jsonify
from flask_cors import CORS
import pandas as pd

import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/execute_python', methods=['POST'])
def execute_python():
    data = request.get_json()
    timetable_data = data.get('timetable')

    # ... rest of your code ... (processing, optimization)

    return jsonify({
        'description': timetable_data,
        'dummy': "olá",
        'mensagem': "BORA"
    })

if __name__ == '__main__':
    app.run(port=5001)