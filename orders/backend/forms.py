from django.forms import ModelForm

from .models import ShopImport


class ShopImportForm(ModelForm):
    class Meta:
        model = ShopImport
        fields = ('user', 'yml_url', )
