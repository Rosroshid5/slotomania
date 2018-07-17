from typing import Type, Dict, Any
from django.db import transaction
from django.http import HttpResponse
# from rest_framework import response
# from rest_framework.generics import GenericAPIView
from django.http import JsonResponse
from django.views import View

from slotomania.contrib.request_resolver import RequestResolver


class InstructorView(View):
    permission_classes: list = []
    routes: Dict[str, Type[RequestResolver]]

    def get(self, request: Any, endpoint: str = None) -> JsonResponse:
        return JsonResponse({})

    @transaction.atomic
    def post(self, request: Any, endpoint: str) -> JsonResponse:
        """If mustate_state returns HttpResponse, return it."""
        resolver = self.routes[endpoint](request=request, data=request.data)
        response = resolver.resolve()
        if isinstance(response, HttpResponse):
            return response
        elif hasattr(response, "sloto_to_dict"):
            return JsonResponse(response.sloto_to_dict())
        elif isinstance(response, dict):
            return JsonResponse(response)
        elif hasattr(response, 'serialize'):
            return JsonResponse(response.serialize())
        else:
            raise AssertionError('Unknow type: {}'.format(type(response)))
