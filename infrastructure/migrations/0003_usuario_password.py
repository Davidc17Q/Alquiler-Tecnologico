# Generated manually — contraseña hasheada para autenticación

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infrastructure", "0002_usuario_rol_activo"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuariomodel",
            name="password",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
    ]
