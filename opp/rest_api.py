from opp import fingerprint_handler
from opp import search
from opp import ftype
from flask import Flask, request
from flask_cors import CORS
from marshmallow import Schema, fields, validate

class FilterSchema(Schema):
    value = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    type = fields.String(required=True, allow_none=True, validate=validate.OneOf([None] + list(set(ftype.SCRAPABLE_TYPES) | set(ftype.SCRAP_RETURN))))
    method = fields.String(required=False, validate=validate.Length(min=1, max=100))
    positive = fields.Boolean(required=True)

class FilterListSchema(Schema):
    filters = fields.List(fields.Nested(FilterSchema()), required=True)

class OPPSearchSchema(Schema):
    target = fields.String(required=False, validate=validate.Length(min=1, max=1000))
    api_key = fields.String(required=False, validate=validate.Length(min=39, max=39))
    cse_id = fields.String(required=False, validate=validate.Length(min=17, max=17))
    depth = fields.Integer(required=False, validate=validate.Range(min=1, max=10))
    active_search = fields.Integer(required=False, validate=validate.OneOf([0, 1]))
    initial_filters = fields.String(required=False)

opp_search_schema = OPPSearchSchema()
filter_list_schema = FilterListSchema()

def run():
    """ This function launches Flask app to serve the REST API of OPP 

    Returns:
        HTTP response
    """
    app = Flask(__name__)
    cors = CORS(app)

    @app.route('/api/', methods=['POST', 'GET'])
    def opp_api():
        # Validation of request arguments
        args = request.args.to_dict()
        errors = opp_search_schema.validate(args)
        if errors:
            return {'errors': errors}, 400

        # Getting arguments if no error
        target = request.args.get('target', None)
        api_key = request.args.get('api_key', None)
        cse_id = request.args.get('cse_id', None)
        depth = int(request.args.get('depth', 3))
        active_search = bool(request.args.get('active_search', 0))

        # Evaluation and validation of initial filters
        try:
            initial_filters = list(eval(request.args.get('initial_filters', '[]')))
        except SyntaxError:
            return {'errors': {"initial_filters":["SyntaxError"]}}, 400
        except NameError:
            return {'errors': {"initial_filters":["NameError"]}}, 400

        errors_filters = filter_list_schema.validate({"filters": initial_filters})
        if errors_filters:
            return {'errors': errors_filters}, 400

        # Request is valid : process it 
        search.SearchOptions(api_key=api_key, cse_id=cse_id, active_search=active_search)
        research_instance = fingerprint_handler.FingerprintHandler(target=target, search_depth=depth, initial_filters = initial_filters)
        fingerprint = research_instance.get_fingerprint()
        return research_instance.get_json_nodes_edges(fingerprint)

    @app.route('/api/status', methods=['GET'])
    def opp_api_status():
        return "OK", 200

    app.run()

if __name__ == '__main__':
    run()
