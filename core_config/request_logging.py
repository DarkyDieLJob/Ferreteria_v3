import threading
import uuid

_thread_locals = threading.local()

def set_request(request):
    _thread_locals.request = request

def get_request():
    return getattr(_thread_locals, "request", None)

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        set_request(request)
        try:
            response = self.get_response(request)
        finally:
            set_request(None)
        return response

class RequestContextFilter:
    def filter(self, record):
        req = get_request()
        if req is not None:
            record.request_id = getattr(req, "request_id", "-")
            user = getattr(req, "user", None)
            if user and getattr(user, "is_authenticated", False):
                record.user = str(user)
            else:
                record.user = "anon"
            meta = getattr(req, "META", {}) or {}
            record.ip = meta.get("HTTP_X_FORWARDED_FOR", meta.get("REMOTE_ADDR", "-"))
        else:
            record.request_id = "-"
            record.user = "-"
            record.ip = "-"
        return True
