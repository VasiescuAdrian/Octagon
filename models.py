from mongoengine import Document, StringField, ListField, BooleanField, DynamicField


class Organization(Document):
    meta = {"collection": "organizations_default",
             "strict": False
                }

    org_id = StringField(required=True)
    name = StringField()
    parent = StringField()
    ancestors = ListField(StringField())
    people = ListField(DynamicField())
    isDeleted = BooleanField(default=False)

    lm_nokia_id = StringField()
    lm_nokia_name = StringField()
    lm_personnel_number = StringField()
    isActingLM = StringField()

    dotted_org_id = StringField()
    sap_org_id = StringField()
    index = DynamicField()
    change_screening_id = ListField(DynamicField())