from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    """
    Декоратор, который проверяет, является ли пользователь администратором.
    Если пользователь - администратор, ему разрешен доступ к представлению.
    В противном случае он будет перенаправлен на страницу входа.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/'
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
