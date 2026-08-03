from rest_framework import serializers

from .models import StartupProfile


class StartupListSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    tags = serializers.SlugRelatedField(
        slug_field="slug",
        many=True,
        read_only=True,
    )

    class Meta:
        model = StartupProfile
        fields = [
            "id",
            "company_name",
            "short_description",
            "thumbnail_url",
            "location",
            "tags",
        ]
