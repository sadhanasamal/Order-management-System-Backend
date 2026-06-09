from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = request.user

        if response.status_code == 200:
            from django.contrib.auth.models import User
            from rest_framework_simplejwt.tokens import AccessToken
            access = AccessToken(response.data['access'])
            user = User.objects.get(id=access['user_id'])
            response.data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_superuser': user.is_superuser,
            }

        return response


class TokenRefreshView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
