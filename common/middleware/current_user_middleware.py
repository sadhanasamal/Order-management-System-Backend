import threading

_thread_locals = threading.local()


class CurrentUserMiddleware:
    """
    Stores the current request in thread-local storage so that BaseModel.save()
    can access request.user without it being passed explicitly through every call.

    Must be placed in MIDDLEWARE after AuthenticationMiddleware so that
    request.user is already resolved by Django/DRF before we store the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            # Always clean up so the thread can be reused cleanly by the pool
            _thread_locals.request = None
        return response


def get_current_request():
    return getattr(_thread_locals, 'request', None)