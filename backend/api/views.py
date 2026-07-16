# from django.shortcuts import render

# # Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class HealthCheck(APIView):
    def get(self, request):
        data = {"status": "ok"}
        return Response(data, status=status.HTTP_200_OK)