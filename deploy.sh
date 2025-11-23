. venv/bin/activate

echo "Информация о ветке"
git branch -a
git rev-parse --abbrev-ref HEAD

#echo "Обновляем ветки"
git add .
git stash
git stash clear
git pull origin

cd app

echo "(requirements) Нажмите 'y' что бы установить из requirements.txt. Enter чтобы пропустить."
read input
if [[ "$input" == "y" ]]; then
  echo "Запуск зависимостей."
  pip install -r ../requirements.txt
fi

echo "(migrate) Нажмите 'y' что бы установить миграции в БД. Enter чтобы пропустить."
read input
if [[ "$input" == "y" ]]; then
  echo "Запуск миграций."
  python manage.py migrate
fi

python manage.py test --keepdb

cd ..

echo "(docker-compose) Нажмите 'y' для перезапуска docker compose, 'b' для ребилда. Enter чтобы пропустить."
read input
if [[ "$input" == "y" ]]; then
  echo "Рестарт docker compose"
  docker compose restart
elif [[ "$input" == "b" ]]; then
  echo "Ребилд docker compose"
  docker compose up --build
else
  echo "Вы отменили перезапуск docker compose."
fi


