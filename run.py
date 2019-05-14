from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from timeout_decorator import timeout
import pg_logger

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
CORS(app)

MAX_TIME_RUNNING = 10

class TimeOutException(Exception):
    pass

@app.route('/api/trace', methods=['POST'])
@cross_origin(origins=['https://rhadamys.pythonanywhere.com', 'http://localhost:8080', 'https://loader.io'])
def request_trace():
    data = request.get_json(force=True)
    try:
        trace = __generate_trace(data)
    except TimeOutException:
        exception = dict(event='instruction_limit_reached',
                         exception_msg='''Tu programa ha estado operando por <u>más de {0} segundos</u>
                         y se ha cancelado su ejecución. Esto puede ocurrir si realizas operaciones con
                         valores muy grandes (Por ejemplo, calcular el <u>factorial de 1000</u>. ¡Qué
                         locura!).'''.format(MAX_TIME_RUNNING),
                         limit='time')
        trace = jsonify([exception])
    return trace

@app.route('/loaderio-d303c47fb9a2d571dd01fa4f9d042c65/')
@cross_origin(origins=['https://loader.io'])
def loader_io():
    return 'loaderio-d303c47fb9a2d571dd01fa4f9d042c65'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cross_origin()
def catch_all(path):
    return render_template("index.html")

# Si generar la traza toma más de MAX_TIME_RUNNING entonces se cancela la operación
@timeout(MAX_TIME_RUNNING, use_signals=False, timeout_exception=TimeOutException)
def __generate_trace(data):
    user_script = data['script']
    raw_input_json = data['raw_input_json'] if 'raw_input_json' in data else None
    trace = pg_logger.exec_script_str_local(user_script, raw_input_json, False, False)
    return jsonify(trace)