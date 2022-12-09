import json
import multiprocessing
import subprocess
import psutil
from multiprocessing import Process
from flask import Blueprint, render_template, request, make_response, Response

views = Blueprint(name="views", import_name="views")


# Other functions
def get_output_subprocess(params, shared_dict):
    """ Gets the stdout and stderr of a subprocess and stores it into a shared_dict """
    cmd = subprocess.run(params, capture_output=True)  # Run the script in a subprocess with all the params
    shared_dict['stdout'] = cmd.stdout.decode()
    shared_dict['stderr'] = cmd.stderr.decode()


# ROUTES
@views.route("/")
def home():
    """ Index of the webapp """
    return render_template('index.html')


@views.route("_ping", methods=['GET'])
def ping():
    return make_response('', 204)


@views.route("/_parse_params", methods=['POST'])
def _parse_params():
    """ This route is called from the front-end each time it needs to talk with the hashcash6 script. The frond-end
    sends a POST request with all the params in a JSON format and this function receives that request, dissects the
    params and passes them to the hashcash6 script returning the output of the script to the front-end. The front-end
    is basically just a wrapper for the back-end cli, not elegant but it works, I didn't want to rewrite the whole
    CLI into JS. """
    response_json = json.loads(request.get_data().decode("utf-8"))  # Get the JSON formatted params from the front-end

    timeout_limit = 30  # Server timeout for request (in seconds)

    params = ["python", "hashcash6"]  # Prepare the parameter list to be sent to the hashcash6 script

    for param in response_json["params"][0]:  # Append the params coming from the front-end to the param_list
        params.append(str(param))

    print(f"Fetching request with params: {params}")

    manager = multiprocessing.Manager()
    shared_dict = manager.dict()
    script_process = Process(
        target=get_output_subprocess,
        args=(params, shared_dict)
    )
    script_process.start()
    script_process.join(timeout_limit)  # If the server doesn't finish the calculation in time we end the calculation

    if script_process.is_alive():  # Means that the process hasn't finished calculating in time
        for child in psutil.Process(script_process.pid).children(recursive=True):  # Kill all the children
            child.kill()
        script_process.kill()
        response = make_response(
            f'[[i;red;]The server took too long to process the command\nCalculation time limit is {timeout_limit}s]',
            200
        )
        response.mimetype = "text/plain"
        return response

    script_stdout = shared_dict['stdout']
    script_stderr = shared_dict['stderr']

    response: Response  # Prepare the response object

    # If the output of the hashcash6 script is a JSON it means that it returned a hashcash6 calculation,
    # if it's not a JSON it means that the output of the script is some text from either a command or an error.
    try:
        script_output = json.loads(script_stdout)
        response = make_response(script_output, 200)
        response.mimetype = "application/json"
    except json.decoder.JSONDecodeError:
        response_text = ''  # Text to be sent in the response

        # Check if either script_stdout or script_stderr are empty, if they are not empty append them to
        # response_text
        if len(script_stdout.strip()) != 0:
            response_text += f'{script_stdout.rstrip()}\n'
        if len(script_stderr.strip()) != 0:
            print(len(script_stderr))
            response_text += f'\n[[;red;]Server returned an error]\n{script_stderr.rstrip()}\n'

        response = make_response(response_text, 200)
        response.mimetype = "text/plain"

    return response
