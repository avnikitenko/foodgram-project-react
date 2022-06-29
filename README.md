# Foodgram
## Описание проекта
Проект Foodgram представляет собой сервис продуктового помощника.  
Доступ к проекту: http://84.201.155.158/  
Админ-панель: http://84.201.155.158/admin/ (login: admin, password: YjdsqGfhjkm1)  
Документация на API: http://84.201.155.158/api/docs/  

## Информация о проекте
Дипломный проект по курсу python-разработчик от Яндекс Практикум.  
Автор: Никитенко Алексей, 27 когорта  
  
![foodgram_workflow.yml](https://github.com/avnikitenko/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
## Локальный запуск проекта
Клонировать репозиторий и перейти в папку infra в командной строке:

```
git clone https://github.com/avnikitenko/foodgram-project-react.git
```

```
cd foodgram-project-react/infra
```

Создать файл .env:

```
touch .env
```

Заполнить .env значениями необходимых переменных окружения:

```
nano .env
```

Наполнение файла env:

```
SECRET_KEY=<hash>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<значение БД>
POSTGRES_USER=<пользователь postgres>
POSTGRES_PASSWORD=<пароль для пользователя postgres>
DB_HOST=<host БД>
DB_PORT=<порт БД>
```

Выполнить сборку docker compose:

```
docker-compose up -d --build
```

Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

Выполнить сборку статики:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

Открыть браузер, перейти на localhost... PROFIT!

## Описание основных разделов сайта
* /admin - панель администратора
* /recipes - список рецептов, содержит следующую функциональность:
  * фильтрация по тегам
  * добавление рецепта в список покупок
  * добавление рецепта в избранное
  * просмотр детальной информации по рецепту с возможностью редактирования
  * просмотр рецептов конкретного автора с возможностью подписаться на рецепта автора
* /subscriptions - список рецептов авторов, на которых подписался авторизованный пользователь
* /recipes/create - форма рецепта с возмонжностью создания нового рецепта
* /favorites - список избранных рецептов пользователя
* /cart - список рецептов в корзине пользователя с возможностью скачать summary всех необходимых ингредиентов для их приготовления
