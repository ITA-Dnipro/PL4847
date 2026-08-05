from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from .models import StartupProfile
from .serializers import StartupListSerializer


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
