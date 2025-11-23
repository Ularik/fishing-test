from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator

from ninja import Router
from ninja_jwt.authentication import JWTAuth
from .schemas import CurrentUserSchema

router = Router()


@router.get("/me", response=CurrentUserSchema, auth=JWTAuth(), summary='Получить информацию о текущем пользователе')
def get_current_user(request):
    """
    Получить информацию о текущем авторизованном пользователе,
    включая его разрешения на редактирование
    """
    user = request.user
    return {
        'id': user.id,
        'user_name': user.user_name,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'is_superuser': user.is_superuser,
        'last_login': user.last_login
    }

# @csrf_exempt
# def login_view(request):
#
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#
#         user = authenticate(request, username=username, password=password)
#
#         if user is not None:
#             login(request, user)
#             return redirect('home')
#
#     return render(request, 'registration/login.html')
#
#
# @method_decorator(csrf_exempt, name='dispatch')
# class CustomLoginView(LoginView):
#
#     template_name = 'registration/login.html'
#
#     def form_valid(self, form):
#         user: CustomUser = form.get_user()
#
#         login(self.request, user)
#
#         return redirect('index')