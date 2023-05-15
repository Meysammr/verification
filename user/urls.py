from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('otp/', views.OTPView.as_view(), name='otp'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/', views.CreatePostView.as_view(), name='create'),
    path('retrive/<slug:slug_id>/', views.RetrievePostView.as_view(), name='read'),
    path('update/<slug:slug_id>/', views.UpdatePostView.as_view(), name='update'),
    path('delete/<slug:slug_id>/', views.DeletePostView.as_view(), name='delete'),
]
