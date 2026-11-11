from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Producto, RespuestaEncuesta, Video


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=False, label="Correo (opcional)")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "categoria", "precio", "talla", "stock", "imagen", "destacado"]


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ["titulo", "descripcion", "url"]


class EncuestaForm(forms.ModelForm):
    satisfaccion = forms.TypedChoiceField(
        label="¿Qué tan satisfecho estás con MAREA? (1 = nada, 5 = muchísimo)",
        choices=RespuestaEncuesta.SATISFACCION,
        coerce=int,
        widget=forms.RadioSelect,
    )
    recomendaria = forms.TypedChoiceField(
        label="¿Nos recomendarías con tus amigos?",
        choices=[(True, "Sí"), (False, "No")],
        coerce=lambda v: v in (True, "True", "true", "1"),
        widget=forms.RadioSelect,
        initial=True,
    )

    class Meta:
        model = RespuestaEncuesta
        fields = ["satisfaccion", "categoria_favorita", "recomendaria", "comentario"]
        labels = {
            "categoria_favorita": "¿Qué categoría te gusta más?",
            "comentario": "¿Algo que quieras contarnos?",
        }
        widgets = {"comentario": forms.Textarea(attrs={"rows": 3})}
