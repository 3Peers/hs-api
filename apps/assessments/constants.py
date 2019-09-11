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
        return [(at.value, at.value) for at in cls]


class ResponseMessages:
    MAX_TEAM_SIZE_LESS_THAN_MIN = 'max team size must be greator than min team size'
    START_TIME_GREATOR_THAN_END = 'start time of the challenge must be earlier than end time'
