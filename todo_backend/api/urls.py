from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('check-auth/', views.check_auth, name='check-auth'),
    path('test-auth/', views.test_auth, name='test-auth'),  # Add this line
    path('todos/', views.todo_list_create, name='todo-list-create'),
    path('todos/<int:pk>/', views.todo_detail, name='todo-detail'),
]