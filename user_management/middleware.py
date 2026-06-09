from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .models import UserPageAssignment

WHITELISTED_PATHS = [
    '/admin/',
    '/static/',
    '/media/',
    '/api/auth/login/',
    '/api/auth/token/refresh/',
    '/api/auth/logout/',
]


class PageAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if any(path.startswith(w) for w in WHITELISTED_PATHS):
            return self.get_response(request)

        auth_header = request.headers.get('Authorization', '')

        if not auth_header.startswith('Bearer '):
            return JsonResponse({'detail': 'Authentication required.'}, status=401)

        raw_token = auth_header.split(' ')[1]

        try:
            token = AccessToken(raw_token)
            user = User.objects.get(id=token['user_id'])
        except (TokenError, InvalidToken):
            return JsonResponse({'detail': 'Token is invalid or expired.'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found.'}, status=401)

        if user.is_superuser:
            return self.get_response(request)

        has_access = UserPageAssignment.objects.filter(
            user=user,
            page__url_path=path,
            page__is_active=True,
        ).exists()

        if not has_access:
            return JsonResponse({'detail': 'You do not have access to this page.'}, status=403)

        return self.get_response(request)
