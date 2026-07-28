from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class LandingContentView(APIView):
    """
    GET /api/content/landing/
    Повертає статичний контент для лендингу (Hero, For Whom, Why Worth, Footer).
    """

    permission_classes = [AllowAny]

    def get(self, request):
        landing_data = {
            "hero": {
                "title": "Платформа для стартапів та інвесторів",
                "subtitle": "Знаходьте інвестиції та запускайте перспективні проєкти разом з нами.",
                "cta_text": "Join",
                "hero_images": [
                    "https://example.com/images/hero1.jpg",
                    "https://example.com/images/hero2.jpg",
                ],
            },
            "for_whom": [
                {
                    "icon": "designer",
                    "title": "Дизайнерам",
                    "desc": "Створюйте круті UI/UX рішення для нових стартапів.",
                },
                {
                    "icon": "developer",
                    "title": "Розробникам",
                    "desc": "Приєднуйтесь до команд та реалізуйте масштабні ідеї.",
                },
                {
                    "icon": "investor",
                    "title": "Інвесторам",
                    "desc": "Знаходьте перспективні стартапи для вкладення коштів.",
                },
            ],
            "why_worth": [
                {
                    "title": "Прозорість",
                    "desc": "Усі умови співпраці прозорі та відкриті.",
                },
                {
                    "title": "Спільнота",
                    "desc": "Доступ до мережі сильних фахівців та менторів.",
                },
            ],
            "footer_links": {
                "left": [
                    {"name": "Про нас", "url": "/about"},
                    {"name": "Контакти", "url": "/contacts"},
                ],
                "right": [
                    {"name": "Privacy Policy", "url": "/privacy"},
                    {"name": "Terms of Service", "url": "/terms"},
                ],
            },
        }
        return Response(landing_data, status=status.HTTP_200_OK)
