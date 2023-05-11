import json
from os import mkdir

from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.authtoken.models import Token

from .models import Case


class API(APIView):
    def post(self, request):
        print(request.POST)
        try:
            cases = request.POST.getlist('cases[]')
            for title in cases:
                current = Case.objects.filter(title=title)
                if len(current) == 0:
                    case = Case(title=title, path='')
                    case.save()
                    mkdir(f'cases/{case.pk}/')
        except MultiValueDictKeyError:
            return Response(
                {'err': 'No cases query parameter'},
                403,
                headers={'Server': 'My server'}
            )

        return Response(
            {
                'err': None,
                'msg': ''
            },
            headers={'Server': 'My server'}
        )
