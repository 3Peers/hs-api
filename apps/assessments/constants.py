from enum import Enum


class AssessmentTypes(Enum):
    HACKATHON = 'hackathon'
    COMPETITIVE_CODING = 'competitive coding'
    SQL = 'sql'
    MACHINE_LEARNING = 'machine learning'
    ARENA = 'arena'
    VIRTUAL = 'virtual'

    @classmethod
    def get_choices(cls):
        return [(at.value, at.value) for at in AssessmentTypes]