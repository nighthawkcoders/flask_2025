from flask import Blueprint, jsonify
from flask_restful import Api, Resource

student_api = Blueprint('student_api', __name__, url_prefix='/api')

# API docs https://flask-restful.readthedocs.io/en/latest/api.html
api = Api(student_api)

class StudentAPI:
    @staticmethod
    def get_student(name):
        students = {
            "John": {
                "name": "John",
                "age": 65,
                "major": "Computer Science",
                "university": "University of Oregon"
            },
            "Jeff": {
                "name": "Jeff",
                "age": 55,
                "major": "Filming Master",
                "university": "ABC University"
            }
        }
        return students.get(name)

    class _John(Resource):
        def get(self):
            # Use the helper method to get John's details
            john_details = StudentAPI.get_student("John")
            return jsonify(john_details)

    class _Jeff(Resource):
        def get(self):
            # Use the helper method to get Jeff's details
            jeff_details = StudentAPI.get_student("Jeff")
            return jsonify(jeff_details)

    class _Bulk(Resource):
        def get(self):
            # Use the helper method to get both John's and Jeff's details
            john_details = StudentAPI.get_student("John")
            jeff_details = StudentAPI.get_student("Jeff")
            return jsonify({"students": [john_details, jeff_details]})

    # Building REST API endpoints
    api.add_resource(_John, '/student/john')
    api.add_resource(_Jeff, '/student/jeff')
    api.add_resource(_Bulk, '/students')
