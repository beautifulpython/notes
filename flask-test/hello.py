from flask import Blueprint
from flask import Response
from datetime import datetime
from flask_restful import reqparse
import json

hello_blueprint = Blueprint("hello", __name__)


@hello_blueprint.route("/")
def root_help():
    res_code = 200
    res_body = {
        "name": "hello",
        "usage": "curl /v1/hello/<user-name>"
    }
    res_body = json.dumps(res_body)
    return Response(response=res_body, status=res_code, mimetype="application/json")


@hello_blueprint.route("/<user_name>")
def hello_user(user_name):
    res_body = json.dumps({
        "name": user_name,
        "time": f"{datetime.now()}"
    })
    return Response(response=res_body, status=200, mimetype="application/json")


@hello_blueprint.route("/add", methods=["POST"])
def hello_add():
    parser = reqparse.RequestParser()
    parser.add_argument("left", type=int, required=True)
    parser.add_argument("right", type=int, required=True)
    args = parser.parse_args()
    res_body = json.dumps({
        "left": args["left"],
        "right": args["right"],
        "sum": args["left"] + args["right"]
    })
    return Response(response=res_body, status=200, mimetype="application/json")
