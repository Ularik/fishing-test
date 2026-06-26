from django.urls import path, include
from .views import get_list, GetList

urlpatterns = [
    path('api/main/list2', GetList.as_view(), name='get_list'), # DRF вариант
]