from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe


def csrf_input_for_request(request):
    """Returns a CSRF hidden input for Jinja2 templates."""
    token = get_token(request)
    return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')
