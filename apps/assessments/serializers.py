from rest_framework import serializers
from .constants import AssessmentTypes, ResponseMessages
from .models import Assessment


class CreateAssessmentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    type = serializers.ChoiceField(choices=AssessmentTypes.get_choices())
    min_team_size = serializers.IntegerField(default=1)
    max_team_size = serializers.IntegerField(default=1)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

    def create(self, validated_data):
        return Assessment.objects.create(**validated_data)

    def validate(self, data):
        if data['max_team_size'] < data['min_team_size']:
            raise serializers.ValidationError(ResponseMessages.MAX_TEAM_SIZE_LESS_THAN_MIN)
        elif data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(ResponseMessages.START_TIME_GREATOR_THAN_END)

        return data
