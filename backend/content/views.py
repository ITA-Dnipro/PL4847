from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class LandingContentView(APIView):
    """API view to serve static landing page content in structured JSON format."""

    permission_classes = (AllowAny,)

    def get(self, request):
        """Handle GET requests and return structured landing content."""
        data = {
            "hero": {
                "title": "Welcome to Startup Platform",
                "subtitle": "Connecting investors and innovative startups.",
                "cta_text": "Join",
                "hero_images": [],
            },
            "for_whom": [
                {
                    "icon": "designer",
                    "title": "Startups",
                    "desc": "Find funding and supporters.",
                },
                {
                    "icon": "investor",
                    "title": "Investors",
                    "desc": "Discover promising ideas.",
                },
            ],
            "why_worth": [
                {
                    "title": "Transparency",
                    "desc": "Verified data and clear analytics.",
                },
                {
                    "title": "Efficiency",
                    "desc": "Streamlined investment process.",
                },
            ],
            "footer_links": {
                "left": [
                    {"name": "About Us", "url": "/about"},
                    {"name": "Privacy Policy", "url": "/privacy"},
                ],
                "right": [
                    {"name": "Contact", "url": "/contact"},
                    {"name": "FAQ", "url": "/faq"},
                ],
            },
        }
        return Response(data, status=status.HTTP_200_OK)
