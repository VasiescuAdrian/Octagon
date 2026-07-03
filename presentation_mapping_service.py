from slide_models import PresentationModel, SlideModel, BoxModel


class PresentationMappingService:
    def build_presentation_model(self, processed_orgs):
        slides = []

        if not processed_orgs:
            return PresentationModel(slides=[])

        for org in processed_orgs:
            org_id = str(org.get("org_id"))
            boxes = []

            print("Creating slide for:", org_id, org.get("name"))

            # Add direct child organizations first.
            direct_children = [
                child
                for child in processed_orgs
                if str(child.get("parent")) == org_id
            ]

            print("Direct children:", len(direct_children))

            for child in direct_children:
                print("  child:", child.get("org_id"), child.get("name"))

                manager = child.get("manager")
                subtitle = "NN"

                if manager:
                    subtitle = manager.get("full_name") or "NN"

                    if manager.get("is_inherited"):
                        subtitle += " (inherited)"

                boxes.append(
                    BoxModel(
                        title=child.get("name") or "Unnamed unit",
                        subtitle=subtitle,
                        box_type="unit",
                        target_org_id=str(child.get("org_id"))
                    )
                )

            # Add direct employees after child units.
            for employee in org.get("employees", []):
                boxes.append(
                    self._employee_to_box(employee)
                )

            slides.extend(
                self._create_slides_for_boxes(
                    org_id=org_id,
                    org_name=org.get("name") or "Organization structure",
                    manager=org.get("manager"),
                    boxes=boxes
                )
            )

        return PresentationModel(slides=slides)

    def _create_slides_for_boxes(self, org_id, org_name, manager, boxes):
        slides = []

        # Split large groups across multiple slides.
        box_chunks = self._split_into_chunks(boxes, chunk_size=15)

        if not box_chunks:
            box_chunks = [[]]

        for index, chunk in enumerate(box_chunks):
            title = org_name

            if len(box_chunks) > 1:
                title = f"{org_name} - part {index + 1}"

            columns = self._split_into_columns(chunk, max_items_per_column=5)

            slide = SlideModel(
                title=title,
                hierarchy_level="",
                head_of_unit=self._manager_to_box(manager),
                columns=columns,
                org_id=org_id
            )

            slides.append(slide)

        return slides

    def _employee_to_box(self, employee):
        title = employee.get("job_title") or "Employee"
        subtitle = employee.get("full_name") or "NN"

        if employee.get("is_acting"):
            subtitle += " (Acting)"

        return BoxModel(
            title=title,
            subtitle=subtitle,
            box_type="unit"
        )

    def _manager_to_box(self, manager):
        if not manager:
            return BoxModel(
                title="Head of unit",
                subtitle="NN",
                box_type="manager"
            )

        title = manager.get("job_title") or "Head of unit"
        subtitle = manager.get("full_name") or "NN"

        if manager.get("is_acting"):
            subtitle += " (Acting)"

        if manager.get("is_inherited"):
            subtitle += " (inherited)"

        return BoxModel(
            title=title,
            subtitle=subtitle,
            box_type="manager"
        )

    def _split_into_columns(self, items, max_items_per_column=5):
        columns = []

        for i in range(0, len(items), max_items_per_column):
            columns.append(items[i:i + max_items_per_column])

        return columns

    def _split_into_chunks(self, items, chunk_size=15):
        chunks = []

        for i in range(0, len(items), chunk_size):
            chunks.append(items[i:i + chunk_size])

        return chunks