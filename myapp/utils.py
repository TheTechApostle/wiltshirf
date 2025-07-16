def is_admin(user):     
    return user.groups.filter(name='admin').exists()

def is_client(user):
    return user.groups.filter(name='client').exists()