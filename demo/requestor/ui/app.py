import os
import json
import subprocess
from flask import Flask, render_template, request
import time

app = Flask(__name__)

# Set the contract address
contract = "secret1c2mfxp0y7sc3fxfknjghx4fr9v97cav3l032kd"


def secretcli(args, json_output=True):
    cmd = ["secretcli"] + args
    if json_output:
        cmd.append("--output=json")
    result = subprocess.check_output(cmd)
    return json.loads(result) if json_output else result


def wait_for_query_change(prev_random):
    while True:
        response = secretcli(["q", "compute", "query", contract, '{"last_random": {}}'])
        if response["random"] != prev_random:
            return response
        time.sleep(1)


@app.route("/")
def index():
    try:
        response = secretcli(["q", "compute", "query", contract, '{"last_random": {}}'])
        random_value = response["random"]
        block_height = response["height"]
    except Exception as e:
        random_value = "Error: {}".format(e)
        block_height = "Error: {}".format(e)

    return render_template("index.html", random_value=random_value, block_height=block_height)


@app.route("/update-random")
def update_random():
    try:
        prev_random = secretcli(["q", "compute", "query", contract, '{"last_random": {}}'])["random"]
        tx = secretcli(["tx", "compute", "execute", contract, '{"do_something": {}}', "--from", "a", "--gas", "200000",
                        "-y"])
        tx_hash = tx["txhash"]
        response = wait_for_query_change(prev_random)
        random_value = response["random"]
        block_height = response["height"]
        return {"random_value": random_value, "block_height": block_height}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
