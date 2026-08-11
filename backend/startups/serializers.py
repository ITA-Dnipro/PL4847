from rest_framework import serializers

from .models import StartupProfile, Subscription


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


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    startup_id = serializers.PrimaryKeyRelatedField(
        source="startup", 
         queryset=StartupProfile.objects.filter(
             status=StartupProfile.Status.PUBLISHED,
        ),
    )

    class Meta:
        model = Subscription
        fields = ["startup_id"]

    def create(self, validated_data):
        user = self.context["request"].user

        subscription, _ = Subscription.objects.get_or_create(
            startup=validated_data["startup"],
            user=user,
        )
        return subscription
