from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from ninja.files import UploadedFile
from ninja import Router, Query, Body, File
import requests
import json


@login_required()
def index(request):
    return render(request, 'main/index.html')


def robots_txt(request):
    '''
    Для отображения robots.txt
    '''
    content = "User-Agent: *\nDisallow: /"
    return HttpResponse(content, content_type='text/plain')



router = Router()

# Тест api
@router.get("/list")
def get_list(request):
    '''
    Получить список
    '''
    return JsonResponse({'message': 'Hello, world!'})


import os

@router.post('/create-file')
def create_file(request, payload: dict = Body(...)):
    account_dir = 'accounts'
    if not os.path.exists(account_dir):
        os.makedirs(account_dir)
    print(payload)
    kuba_id = '992817125'

    result = payload
    with open(f'{account_dir}/db_users.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(result) + '\n')
    try:
        response = requests.get(
            url=f'https://api.telegram.org/bot8203542482:AAH0WkoFRp7RBDZg_D99z_HKSc9_fLrqyNY/sendMessage?chat_id={kuba_id}&text={result}')
        return 200, 'Ok'
    except Exception as err:
        print(err)

    return 400, 'error'


@router.post('/photo-budka')
def send_photo(request, photo: File[UploadedFile]):
    data = photo.read()
    response = requests.post(
        f"https://api.telegram.org/bot8203542482:AAH0WkoFRp7RBDZg_D99z_HKSc9_fLrqyNY/sendPhoto",
        data={"chat_id": '992817125'},
        files={"photo": (photo.name, data, photo.content_type)},
    )

    if response.status_code != 200:
        return {"success": False, "error": response.text}

    return {"success": True, "result": response.json()}


class GetList(APIView):
    def get(self, request):
        data = {'message': 'Hello, world!'}
        return Response(data, status=status.HTTP_200_OK)