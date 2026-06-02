import logging

logger = logging.getLogger(__name__)

class AuthDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        is_auth = request.user.is_authenticated
        user = request.user
        session_key = request.session.session_key
        
        print(f"\n[TRACE] REQUEST START: {path}")
        print(f" - User: {user}")
        print(f" - Is Authenticated: {is_auth}")
        print(f" - Session Key: {session_key}")
        print(f" - Cookies: {list(request.COOKIES.keys())}")

        response = self.get_response(request)

        print(f"[TRACE] REQUEST END: {path} -> STATUS {response.status_code}")
        if 'Location' in response:
            print(f" - Redirecting to: {response['Location']}")
        
        return response
