# Generated manually for usuario rol/activo

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("infrastructure", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuariomodel",
            name="activo",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="usuariomodel",
            name="rol",
            field=models.CharField(
                choices=[
                    ("CLIENTE", "CLIENTE"),
                    ("VENDOR", "VENDOR"),
                    ("ADMIN", "ADMIN"),
                ],
                default="CLIENTE",
                max_length=20,
            ),
        ),
    ]
