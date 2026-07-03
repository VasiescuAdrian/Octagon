from typing import List, Dict, Optional, Any


def get_value(item: Any, field: str, default=None):
    
    if item is None:
        return default

    if isinstance(item, dict):
        return item.get(field, default)

    return getattr(item, field, default)


class BusinessLogicService:
    def __init__(self, include_externals: bool = False, include_trainees: bool = False):
        self.include_externals = include_externals
        self.include_trainees = include_trainees

    def process_data(self, raw_orgs: List) -> List[Dict]:
        
        if not raw_orgs:
            return []

        active_orgs = [
            org for org in raw_orgs
            if not get_value(org, "isDeleted", False)
        ]

        org_map = {
            str(get_value(org, "org_id")): org
            for org in active_orgs
        }

        processed_results = []

        for org in active_orgs:
            unit_data = {
                "org_id": get_value(org, "org_id"),
                "name": get_value(org, "name") or "Unnamed organization",
                "parent": get_value(org, "parent"),
                "manager": None,
                "employees": []
            }

            people = get_value(org, "people", []) or []

            for person in people:
                if self._should_include_person(person, org):
                    mapped_person = self._map_person(person, org)

                    if self._is_manager_for_org(person, org):
                        mapped_person["is_head"] = True
                        mapped_person["is_inherited"] = False
                        unit_data["manager"] = mapped_person
                    else:
                        unit_data["employees"].append(mapped_person)

            if unit_data["manager"] is None:
                unit_data["manager"] = self._find_manager_in_ancestors(
                    org=org,
                    org_map=org_map
                )

            processed_results.append(unit_data)

        return processed_results

    def _should_include_person(self, person, org) -> bool:
        
        if self._is_manager_for_org(person, org):
            return True

        headcount_status = (get_value(person, "HEADCOUNT_STATUS", "") or "").strip().lower()
        if headcount_status in ("2", "not in headcount"):
            return False

        status = (get_value(person, "STATUS", "") or "").strip().lower()
        if status == "inactive":
            return False

        group_text = (get_value(person, "EMPLOYEE_GROUP_TEXT", "") or "").strip().lower()
        external_type = (get_value(person, "EXTERNAL_TYPE", "") or "").strip().lower()

        is_external = (
            any(x in group_text for x in ["external", "etl", "contractor"])
            or bool(external_type)
        )

        if is_external and not self.include_externals:
            return False

        is_trainee = any(
            x in group_text
            for x in ["trainee", "student", "intern", "apprentice"]
        )

        if is_trainee and not self.include_trainees:
            return False

        return True

    def _is_manager_for_org(self, person, org) -> bool:
       
        personnel_number = str(get_value(person, "PERSONNEL_NUMBER", "") or "")
        org_lm_number = str(get_value(org, "lm_personnel_number", "") or "")

        if personnel_number and org_lm_number and personnel_number == org_lm_number:
            return True

        line_manager = (get_value(person, "LineManager", "") or "").strip().lower()

        return line_manager in ("y", "yes", "true", "1")

    def _find_manager_in_ancestors(self, org, org_map: Dict[str, Any]) -> Optional[Dict]:
        """
        Dacă organizația nu are manager direct, urcă în ancestors.

        ancestors este de forma:
            [root, ..., parent]

        De aceea mergem invers, ca să începem cu părintele direct.
        """
        ancestors = get_value(org, "ancestors", []) or []

        for ancestor_id in reversed(ancestors):
            ancestor_org = org_map.get(str(ancestor_id))

            if not ancestor_org:
                continue

            people = get_value(ancestor_org, "people", []) or []

            for person in people:
                if self._is_manager_for_org(person, ancestor_org):
                    mapped_manager = self._map_person(person, ancestor_org)
                    mapped_manager["is_head"] = True
                    mapped_manager["is_inherited"] = True
                    mapped_manager["inherited_from_org_id"] = get_value(ancestor_org, "org_id")
                    mapped_manager["inherited_from_org_name"] = get_value(ancestor_org, "name")
                    return mapped_manager

        return None

    def _map_person(self, person, org) -> Dict:
        """
        Transformă persoana brută într-un format simplu pentru PPT.
        """
        first_name = get_value(person, "FirstName")
        last_name = get_value(person, "LastName")
        full_name = get_value(person, "Name")

        if not full_name:
            full_name = f"{first_name or ''} {last_name or ''}".strip()

        if not full_name:
            full_name = "Unknown"

        city = get_value(person, "City")
        country = get_value(person, "Country")

        location_parts = [part for part in [city, country] if part]
        location = ", ".join(location_parts) if location_parts else "N/A"

        is_acting = False
        if self._is_manager_for_org(person, org):
            is_acting = str(get_value(org, "isActingLM", "false") or "").lower() == "true"

        return {
            "full_name": full_name,
            "job_title": get_value(person, "JOB_TITLE") or "N/A",
            "email": get_value(person, "Email"),
            "location": location,
            "country": country,
            "city": city,
            "personnel_number": get_value(person, "PERSONNEL_NUMBER"),
            "nsn_id": get_value(person, "NSN_ID"),
            "team_code": get_value(person, "TeamCode"),
            "is_head": False,
            "is_acting": is_acting,
            "is_inherited": False
        }