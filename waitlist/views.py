from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Waitlist
from .serializers import WaitlistSerializer  

class PostWaitlistAPIView(APIView):
    def post(self, request):
        serializer = WaitlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "You're on the list! 🎉",
                "position": Waitlist.objects.count()
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListWaitlistAPIView(APIView):
    def get(self, request):
        count = Waitlist.objects.count()
        return Response({"total_on_waitlist": count})