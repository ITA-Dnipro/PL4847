from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StartupProfile
from .serializers import StartupListSerializer, SubscriptionCreateSerializer


class StartupPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    max_page_size = 50


class StartupListView(ListAPIView):

    serializer_class = StartupListSerializer
    pagination_class = StartupPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            StartupProfile.objects.filter(status=StartupProfile.Status.PUBLISHED)
            .select_related("location")
            .prefetch_related("tags")
            .order_by("company_name", "id")
        )

        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(company_name__icontains=search)

        return queryset.distinct()


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SubscriptionCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Subscribed."}, status=status.HTTP_201_CREATED)
