from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from .serializers import CreateAssessmentSerializer


class CreateAssessmentView(APIView):
    permissions = (IsAuthenticated,)

    def post(self, request):
        serializer = CreateAssessmentSerializer(data=request.data)
        if serializer.is_valid():
            assessment = serializer.save(creator=request.user)
            return Response({
                'name': assessment.name,
                'type': assessment.type,
                'min_team_size': assessment.min_team_size,
                'max_team_size': assessment.max_team_size,
                'start_time': assessment.start_time,
                'end_time': assessment.end_time
            })
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
