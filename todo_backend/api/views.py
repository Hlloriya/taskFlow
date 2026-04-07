from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import Todo
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    TodoSerializer
)

@api_view(['POST'])
@csrf_exempt
def register(request):
    """User Registration API"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Registration successful',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
def user_login(request):
    """User Login API"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']
        
        # Check if input is email or username
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                username = user.username
            except User.DoesNotExist:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            username = username_or_email
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
def user_logout(request):
    """User Logout API"""
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def check_auth(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return Response({
            'authenticated': True, 
            'user_id': request.user.id,
            'username': request.user.username
        }, status=status.HTTP_200_OK)
    return Response({'authenticated': False}, status=status.HTTP_200_OK)

@api_view(['GET'])
def test_auth(request):
    """Test authentication endpoint"""
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user_id': request.user.id,
            'username': request.user.username,
            'session_key': request.session.session_key
        })
    return Response({
        'authenticated': False,
        'session_key': request.session.session_key
    })

@api_view(['GET', 'POST'])
def todo_list_create(request):
    """Get all todos or create new todo"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        todos = Todo.objects.filter(user=request.user)
        serializer = TodoSerializer(todos, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TodoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def todo_detail(request, pk):
    """Get, update or delete a specific todo"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        todo = Todo.objects.get(pk=pk, user=request.user)
    except Todo.DoesNotExist:
        return Response({'error': 'Todo not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TodoSerializer(todo)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TodoSerializer(todo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        todo.delete()
        return Response({'message': 'Todo deleted successfully'}, status=status.HTTP_200_OK)