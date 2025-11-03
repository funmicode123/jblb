from rest_framework.response import Response
from rest_framework import status, generics
from clubs.serializers import ClubSerializer
from clubs.services.club_service import create_club
class CreateClubView(generics.CreateAPIView):
    serializer_class = ClubSerializer
    def post(self, request, *args, **kwargs):
        owner = request.user
        data = request.data

        result = create_club(
            name=data.get("name"),
            owner=owner,
            owner_wallet=data.get("owner_wallet"),
            category=data.get("category", "common"),
            tier=data.get("tier", "COMMON"),
            access_type=data.get("access_type", "Free"),
            privileges=data.get("privileges", ""),
        )

        # Handle insufficient token balance
        if result.get("status") == "failed":
            return Response(result, status=status.HTTP_403_FORBIDDEN)

        return Response(result, status=status.HTTP_201_CREATED)
