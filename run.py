from flask import Flask, render_template, request,jsonify
from flask_cors import CORS
import pg_logger

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
CORS(app)

@app.route('/trace', methods=['POST'])
def generate_trace():
    data = request.get_json(force=True)
    user_script = data['script']
    raw_input_json = data['raw_input_json'] if 'raw_input_json' in data else None
    trace = pg_logger.exec_script_str_local(user_script, raw_input_json, False, False)
    return jsonify(trace)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")