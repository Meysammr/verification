import os

from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from redis import Redis
from random import randint

from .serializers import *
from .tasks import send_otp
from .models import Post
from .permissions import IsOwnerOrReadOnly

redis_connection = Redis(host='localhost', port=6379, db=0, decode_responses=True, charset='UTF-8')

API_KEY = os.environ.get('API_KEY')


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []


    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get('phone_number')
        get_phone = redis_connection.get(phone_number)
        if get_phone is None:
            verification_code = str(randint(10000, 99999))
            send_otp.apply_async(args=[phone_number, verification_code])
            return Response({'result': 'OK'}, status=status.HTTP_200_OK)
        else:
            return Response(get_phone, status=status.HTTP_404_NOT_FOUND)


class OTPView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone_number']
        otp_2=redis_connection.get(phone)

        otp_code = serializer.validated_data.get('otp_code')

        if str(otp_2) == str(otp_code):
            user, created = User.objects.get_or_create(username=phone)
            refresh_token = RefreshToken().for_user(user)
            access_token = refresh_token.access_token
            data = {'access_token': str(access_token), 'refresh_token': str(refresh_token)}
            return Response(data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class HomeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response('OK', status=status.HTTP_200_OK)


class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data['title']
        text = serializer.validated_data['text']
        if Post.objects.filter(title=title).exists():
            return Response(data={'error':'this title has already exists'}, status=status.HTTP_409_CONFLICT)
        Post.objects.create(text=text, title=title, owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RetrievePostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request ,slug_id):
        try:
            post = Post.objects.get(slug=slug_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        response_data = {
            "User": post.owner.username,
            "title": post.title,
            "text": post.text,
            "created_at": post.created_at,
            "modified_at": post.modified_at,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
        

class UpdatePostView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def put(self, request,slug_id):
        try:
            post = Post.objects.get(slug=slug_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if post.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if post.objects.filter(title=serializer.validated_data['title']).exists():
            return Response(status=status.HTTP_409_CONFLICT)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
        


class DeletePostView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def delete(self, request,slug_id):
        try:
            post = Post.objects.get(slug=slug_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response(status=status.HTTP_200_OK)