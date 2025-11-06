from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from clubs.serializers import ClubSerializer


class CreateClubView(generics.CreateAPIView):
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        club = serializer.save()
        return Response(self.get_serializer(club).data, status=status.HTTP_201_CREATED)
