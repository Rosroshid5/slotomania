from typing import Type, Dict
from django.db import transaction
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from slotomania.contrib.request_resolver import RequestResolver


class InstructorView(GenericAPIView):
    permission_classes: list = []
    routes: Dict[str, Type[RequestResolver]]

    def get(self, request, endpoint: str = None):
        return Response({})

    @transaction.atomic
    def post(self, request, endpoint: str) -> Response:
        """If mustate_state returns HttpResponse, return it."""
        resolver = self.routes[endpoint](request=request, data=request.data)
        response = resolver.resolve()
        if isinstance(response, HttpResponse):
            return response
        elif hasattr(response, "sloto_to_dict"):
            return Response(response.sloto_to_dict())
        elif isinstance(response, dict):
            return Response(response)
        elif hasattr(response, 'serialize'):
            return Response(response.serialize())
        else:
            raise AssertionError('Unknow type: {}'.format(type(response)))
