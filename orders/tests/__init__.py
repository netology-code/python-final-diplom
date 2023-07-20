import os 
import django 

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")
django.setup()