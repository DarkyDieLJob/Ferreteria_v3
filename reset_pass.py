import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
import django
django.setup()
from django.contrib.auth.models import User
def reset(username, contraseña):
    u = User.objects.get(username=username)
    u.set_password(contraseña)
    u.save()

if __name__ == "__main__":
    reset(input("usuario"),input("contraseña"))