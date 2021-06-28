from django.urls import path

from . import views

app_name = 'articles'
urlpatterns = [
	path('<int:id1>-<int:id2>/',views.index,name='index'),
	path('main/',views.main,name='main'),
	path('update/',views.update,name='update'),
]
