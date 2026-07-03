import os

from flask import Blueprint, request, jsonify, render_template, send_from_directory

from request_models import GenerateRequestPpt
from response_models import GenerateResponsePpt


def create_generation_blueprint(generation_service):
    generation_bp = Blueprint('generation', __name__)

    @generation_bp.route("/", methods=['GET'])
    def index():
        return render_template("index.html")

    @generation_bp.route("/generated/<path:filename>", methods=['GET'])
    def download_generated(filename):
        # Serve the generated PPTX files. output_dir is configured on the
        # ppt_service; fall back to the conventional "generated" folder.
        output_dir = getattr(
            getattr(generation_service, "ppt_service", None),
            "output_dir",
            "generated"
        )
        return send_from_directory(
            os.path.abspath(output_dir),
            filename,
            as_attachment=True
        )

    @generation_bp.route("/api/search-orgs", methods=['GET'])
    def search_orgs():
        # Live search for organizations by name across ALL data collections
        # Returns {org_id, name, collection_name} for the autocomplete dropdown.
        query = request.args.get("q", "").strip()

        if len(query) < 2:
            # Avoid huge result sets on very short queries.
            return jsonify({"results": []}), 200

        try:
            repo = generation_service.org_repository
            results = repo.search_orgs_all_collections(query)
            return jsonify({"results": results}), 200
        except Exception as error:
            return jsonify({"results": [], "message": str(error)}), 500

    @generation_bp.route("/api/generate", methods=['POST'])
    def generate_ppt():
        try:
            body = request.get_json()
            
            if body is None:
                response = GenerateResponsePpt(
                    success=False,
                    message = "Request body is missing or not in JSON format"
                )
                return jsonify(response.__dict__), 400

            if "org_id" not in body or not body["org_id"]:
                response = GenerateResponsePpt(
                success = False,
                message = "org_id is required and cannot be empty"
                )
                return jsonify(response.__dict__), 400
            

            if "collection_name" not in body or not body["collection_name"]:
                response = GenerateResponsePpt(
                    success=False,
                    message="Missing required field: collection_name"
                )
                return jsonify(response.__dict__), 400


            generate_request = GenerateRequestPpt(
                org_id = body["org_id"],
                collection_name = body["collection_name"],
                include_externals = body.get("include_externals", False),
                include_trainees = body.get("include_trainees", False),
                template_name = body.get("template_name", "default"),
                output_name = body.get("output_name"),
                colors = body.get("colors")
            )

            generated_file = generation_service.generate(generate_request)

            response = GenerateResponsePpt(
                success = True, 
                file_url = generated_file.file_url,
                message = "PPT generated successfully"
            )

            return jsonify(response.__dict__), 200

        except ValueError as error:
            response = GenerateResponsePpt(
                success = False, 
                message = str(error)
            )

            return jsonify(response.__dict__), 400

        except Exception as error:
            response = GenerateResponsePpt(
                success = False, 
                message = "An unexpected error occurred: " + str(error)
            )

            return jsonify(response.__dict__), 500
        
    return generation_bp