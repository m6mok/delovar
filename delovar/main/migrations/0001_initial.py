# Generated by Django 4.2 on 2023-11-05 17:24

from django.db import migrations, models
import main.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('receipt', models.FileField(blank=True, null=True, upload_to=main.models.file_path, verbose_name='Квитанция об уплате госпошлины')),
                ('statement', models.FileField(blank=True, null=True, upload_to=main.models.file_path, verbose_name='Заявление')),
                ('debt_statement', models.FileField(upload_to=main.models.file_path, verbose_name='Расчеты по задолженности')),
                ('egrn', models.FileField(blank=True, null=True, upload_to=main.models.file_path, verbose_name='Выписка из ЕГРН')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Дело',
                'verbose_name_plural': 'Дела',
            },
        ),
    ]