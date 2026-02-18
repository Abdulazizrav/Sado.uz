from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

# Pricing plans and categories passed to template via TemplateView
PRICING_PLANS = [
    {
        'name': 'Basic',
        'price': 'Bepul',
        'period': '14 kunlik sinov',
        'popular': False,
        'features': ['20 ta manba', '50 yangilik/kun', 'Telegram bot', '3 kategoriya'],
    },
    {
        'name': 'Standard',
        'price': '299K',
        'period': "so'm / oy",
        'popular': True,
        'features': ['100+ manba', '500 yangilik/kun', 'API + Telegram', 'Barcha kategoriyalar', 'Admin panel', 'AutoPosting'],
    },
    {
        'name': 'Enterprise',
        'price': 'Kelishuv',
        'period': 'asosida',
        'popular': False,
        'features': ['1000+ manba', 'Cheksiz yangilik', 'Maxsus API', 'Custom AI modeli', 'Video yangiliklar', 'Dedicated support'],
    },
]

NEWS_CATEGORIES = [
    {'icon': '🌍', 'label': 'Jahon siyosati'},
    {'icon': '💰', 'label': 'Iqtisodiyot'},
    {'icon': '⚽', 'label': 'Sport'},
    {'icon': '💻', 'label': 'Texnologiya'},
    {'icon': '🏥', 'label': "Sog'liqni saqlash"},
    {'icon': '🎬', 'label': 'Madaniyat'},
    {'icon': '🌱', 'label': 'Ekologiya'},
    {'icon': '📈', 'label': 'Moliya & Bozorlar'},
    {'icon': '🔬', 'label': 'Fan'},
    {'icon': '🚀', 'label': 'Kosmik tadqiqotlar'},
    {'icon': '🛡️', 'label': 'Xavfsizlik'},
    {'icon': '🎓', 'label': "Ta'lim"},
]


def home_view(request):
    from django.shortcuts import render
    return render(request, 'index.html', {
        'plans': PRICING_PLANS,
        'categories': NEWS_CATEGORIES,
    })


def contact_submit(request):
    """
    Form submission endpoint — ready for backend integration.
    Uncomment the DB save block when models are added.
    """
    import json
    from django.http import JsonResponse
    from django.views.decorators.http import require_POST

    if request.method != 'POST':
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['POST'])

    try:
        data = json.loads(request.body)
        # TODO: uncomment when backend models are ready
        # from .models import ContactRequest
        # ContactRequest.objects.create(
        #     name=data.get('name', ''),
        #     company=data.get('company', ''),
        #     email=data.get('email', ''),
        #     phone=data.get('phone', ''),
        #     platform=data.get('platform', ''),
        #     plan=data.get('plan', 'standard'),
        #     message=data.get('message', ''),
        # )
        return JsonResponse({'status': 'ok', 'message': 'Ariza qabul qilindi!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('contact/', contact_submit, name='contact_submit'),
]