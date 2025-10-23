from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
class ProfileView(APIView):
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        if not user:
            return Response({'detail':'unauthenticated'}, status=401)
        return Response(UserSerializer(user).data)
