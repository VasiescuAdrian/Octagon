class GeneratedFile:
    def __init__(self, file_url: str):
        self.file_url = file_url


class GenerationService:
    def __init__(
        self,
        org_repository,
        business_logic_service_class,
        presentation_mapping_service,
        ppt_service
    ):
        self.org_repository = org_repository
        self.business_logic_service_class = business_logic_service_class
        self.presentation_mapping_service = presentation_mapping_service
        self.ppt_service = ppt_service

    def generate(self, request):
        orgs = self.org_repository.get_org_with_hierarchy(
            request.org_id,
            request.collection_name
        )

        if not orgs:
            raise ValueError(
                f"No organization found for org_id={request.org_id} "
                f"in collection={request.collection_name}"
            )

        business_logic_service = self.business_logic_service_class(
            include_externals=request.include_externals,
            include_trainees=request.include_trainees
        )

        processed_orgs = business_logic_service.process_data(orgs)

        if not processed_orgs:
            raise ValueError("Failed to process organization data")

        presentation_model = self.presentation_mapping_service.build_presentation_model(
            processed_orgs
        )

        file_url = self.ppt_service.generate_presentation(
            model=presentation_model,
            template_name=request.template_name,
            output_name=request.output_name,
            colors=getattr(request, "colors", None)
        )

        if not file_url:
            raise ValueError("Failed to generate presentation file URL")

        return GeneratedFile(file_url)