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
                    "icon": "pen",
                    "title": "Виробники крафтової продукції",
                    "desc": "Розширюйте канали збуту та знаходьте нових партнерів.",
                },
                {
                    "icon": "wine",
                    "title": "Сомельє та ресторатори",
                    "desc": "Підбирайте перевірені позиції для своєї карти напоїв.",
                },
                {
                    "icon": "hotel",
                    "title": "Представники готельно-ресторанного бізнесу",
                    "desc": "Формуйте асортимент для закладів гостинності.",
                },
                {
                    "icon": "cart",
                    "title": "Представники роздрібних та гуртових торгових мереж",
                    "desc": "Знаходьте перевірених постачальників для мережі.",
                },
                {
                    "icon": "box",
                    "title": "Представники пакувальної індустрії",
                    "desc": "Пропонуйте пакувальні рішення виробникам.",
                },
                {
                    "icon": "truck",
                    "title": "Представники логістичних компаній та служб доставки",
                    "desc": "Забезпечуйте доставку продукції між учасниками ринку.",
                },
                {
                    "icon": "rocket",
                    "title": "Стартапери",
                    "desc": "Тестуйте та масштабуйте нові продукти на платформі.",
                },
                {
                    "icon": "people",
                    "title": "Інші фахівці галузі",
                    "desc": "Долучайтеся, якщо працюєте у суміжних напрямках галузі.",
                },
            ],
            "why_worth": [
                {
                    "title": "Прямий зв'язок з виробниками",
                    "desc": "Знайомтеся з історією та цінностями брендів",
                },
                {
                    "title": "Ексклюзивні пропозиції",
                    "desc": "Знаходьте унікальні продукти, недоступні в масовому продажі",
                },
                {
                    "title": "Інновації та тренди",
                    "desc": "Будьте в курсі останніх новинок та технологій галузі",
                },
                {
                    "title": "Співпраця та синергія",
                    "desc": "Об'єднуйтесь, щоб творити нове та ділитися досвідом",
                },
                {
                    "title": "Розвиток та масштабування",
                    "desc": "Знаходьте нових партнерів, клієнтів та ринки збуту ",
                },
                {
                    "title": "Підтримка та знання",
                    "desc": "Отримуйте консультації, експертну допомогу та доступ до освітніх ресурсів",
                },
            ],
            "footer_links": {
                "left": [
                    {"name": "Компанії", "url": "/companies"},
                    {"name": "Стартапи", "url": "/startups"},
                ],
                "right": [
                    {"name": "Contact", "url": "/contact"},
                    {"name": "FAQ", "url": "/faq"},
                    {"name": "Виробники", "url": "/manufacturers"},
                    {"name": "Імпортери", "url": "/importers"},
                    {"name": "Роздрібні мережі", "url": "/retail-chains"},
                    {"name": "HORECA", "url": "/horeca"},
                    {"name": "Інші послуги", "url": "/other-services"},
                ],
            },
        }
        return Response(data, status=status.HTTP_200_OK)
