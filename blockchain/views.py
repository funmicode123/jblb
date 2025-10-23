from rest_framework.views import APIView
from rest_framework.response import Response
from .anoma_service import publish_intent
from .hedera_service import publish_to_hcs, create_fungible_token
class AnomaIntentView(APIView):
    def post(self, request):
        r = publish_intent(request.data); return Response(r)
class HederaPublishView(APIView):
    def post(self, request):
        r = publish_to_hcs(request.data.get('topic'), request.data.get('message', {})); return Response(r)
