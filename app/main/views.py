from http.client import HTTPException
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from ninja.files import UploadedFile
from ninja import Router, Body, File
import requests
import json
import os


router = Router()


@router.get("/list")
def get_list(request):
    '''
    Получить список
    '''
    return JsonResponse({'message': 'Hello, world!'})


@router.post('/create-file')
def create_file(request, payload: dict = Body(...)):
    account_dir = 'accounts'
    if not os.path.exists(account_dir):
        os.makedirs(account_dir)
    kuba_id = settings.CHAT_ID

    result = payload
    with open(f'{account_dir}/db_users.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(result) + '\n')
    try:
        requests.get(
            url=f'{settings.TELEGRAM_API}{settings.BOT_ID}/sendMessage?chat_id={kuba_id}&text={result}')
        return 200, 'Ok'
    except Exception as err:
        raise HTTPException(err)


@router.post('/photo-budka')
def send_photo(request, photo: File[UploadedFile]):
    data = photo.read()
    response = requests.post(
        f"{settings.TELEGRAM_API}{settings.BOT_ID}/sendPhoto",
        data={"chat_id": settings.CHAT_ID},
        files={"photo": (photo.name, data, photo.content_type)},
    )

    if response.status_code != 200:
        return {"success": False, "error": response.text}

    return {"success": True, "result": response.json()}


class GetList(APIView):
    def get(self, request):
        data = {'message': 'Hello, world!'}
        return Response(data, status=status.HTTP_200_OK)