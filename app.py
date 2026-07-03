from flask import Flask
from mongoengine import connect

from routes import create_generation_blueprint
from generation_service import GenerationService
from DataAccessLayer import DataAccessLayer
from BusinessLogicService import BusinessLogicService
from presentation_mapping_service import PresentationMappingService
from ppt_service import PptService


def create_app():
    # Flask's default "templates" folder would clash with the PPTX template
    # directory, so HTML lives in "web" instead.
    app = Flask(__name__, template_folder="web")

    # Connect to local MongoDB database restored from testDB.zip
    connect(
        db="testDB",
        host="localhost",
        port=27017
    )

    ppt_service = PptService(
        template_dir="templates",
        output_dir="generated",
        base_url="http://localhost:5000/generated"
    )

    presentation_mapping_service = PresentationMappingService()

    generation_service = GenerationService(
        org_repository=DataAccessLayer,
        business_logic_service_class=BusinessLogicService,
        presentation_mapping_service=presentation_mapping_service,
        ppt_service=ppt_service
    )

    generation_bp = create_generation_blueprint(generation_service)
    app.register_blueprint(generation_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)