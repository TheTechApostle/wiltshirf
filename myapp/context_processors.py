def user_info(request):
    if request.user.is_authenticated:
        return {
            'user_username': request.user.username,
            # 'user_firstname': request.user.first_name,
        }
    return {}
