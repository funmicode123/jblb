from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Club
from .serializers import ClubSerializer
from .services import create_club
class CreateClubView(APIView):
    def post(self, request):
        data = request.data
        name = data.get('name'); owner = data.get('owner_wallet')
        if not name or not owner: return Response({'error':'name and owner_wallet required'}, status=400)
        nft = create_club(name, owner)
        club = Club.objects.create(name=name, owner_wallet=owner, nft_id=nft.get('match_id') if isinstance(nft, dict) else None)
        return Response(ClubSerializer(club).data)
