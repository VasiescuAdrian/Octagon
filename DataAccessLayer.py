from mongoengine.context_managers import switch_collection
from mongoengine.connection import get_db
from models import Organization


class DataAccessLayer:
    @staticmethod
    def get_org_by_id(org_id, collection_name):
        org_id = str(org_id)
        collection_name = str(collection_name)

        with switch_collection(Organization, collection_name) as Org:
            return Org.objects(org_id=org_id).first()

    @staticmethod
    def get_sub_organizations(parent_id, collection_name):
        parent_id = str(parent_id)
        collection_name = str(collection_name)

        with switch_collection(Organization, collection_name) as Org:
            return list(Org.objects(parent=parent_id))

    @staticmethod
    def get_data_collection_names(headers_collection="headers"):
        """
        Read the list of real org-data collections from the `headers`
        collection. Each headers document has a `collection_name` field that
        points to an actual data collection.
        """
        db = get_db()
        names = db[headers_collection].distinct("collection_name")
        # Keep only non-empty string names.
        return [str(n) for n in names if n]

    @staticmethod
    def search_orgs_by_name(query, collection_name, limit=15):
        """
        Search organizations whose name contains `query` (case-insensitive),
        within the given collection. Returns a list of {org_id, name} dicts.
        """
        query = str(query or "").strip()
        collection_name = str(collection_name)

        if not query:
            return []

        with switch_collection(Organization, collection_name) as Org:
            matches = Org.objects(
                name__icontains=query
            ).only("org_id", "name").limit(limit)

            return [
                {"org_id": str(org.org_id), "name": org.name}
                for org in matches
            ]

    @staticmethod
    def search_orgs_all_collections(query, limit=20, headers_collection="headers"):
        """
        Search organizations by name across every data collection listed in
        `headers`. Returns a list of {org_id, name, collection_name}, so the
        caller knows which collection each match belongs to.

        De-duplicates by org_id: each organization appears only once, even if
        it exists in several collections (the first collection found wins).
        Stops once `limit` unique results are collected.
        """
        query = str(query or "").strip()

        if not query:
            return []

        collection_names = DataAccessLayer.get_data_collection_names(headers_collection)

        results = []
        seen_org_ids = set()

        for collection_name in collection_names:
            if len(results) >= limit:
                break

            try:
                with switch_collection(Organization, collection_name) as Org:
                    matches = Org.objects(
                        name__icontains=query
                    ).only("org_id", "name").limit(limit)

                    for org in matches:
                        org_id = str(org.org_id)

                        # Skip if we've already seen this org in another
                        # (or the same) collection.
                        if org_id in seen_org_ids:
                            continue
                        seen_org_ids.add(org_id)

                        results.append({
                            "org_id": org_id,
                            "name": org.name,
                            "collection_name": collection_name
                        })

                        if len(results) >= limit:
                            break
            except Exception:
                # Skip collections that fail (e.g. unexpected schema) rather
                # than breaking the whole search.
                continue

        return results

    @staticmethod
    def get_org_with_hierarchy(org_id, collection_name):
        org_id = str(org_id)
        collection_name = str(collection_name)

        print("Searching org_id:", org_id)
        print("Using collection:", collection_name)

        with switch_collection(Organization, collection_name) as Org:
            print("Collection count:", Org.objects.count())

            root_org = Org.objects(org_id=org_id).first()

            if root_org:
                print("Found root:", root_org.org_id, root_org.name)
            else:
                print("Found root: None")

            if not root_org:
                return []

            descendants = list(Org.objects(ancestors=org_id))

            print("Descendants count:", len(descendants))
            for descendant in descendants:
                print("Descendant:", descendant.org_id, descendant.name)

            return [root_org] + descendants