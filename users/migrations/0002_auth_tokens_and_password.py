# Migração para adicionar autenticação simples por senha e token.

import django.db.models.deletion
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
from django.utils import timezone


def set_default_passwords(apps, schema_editor):
    User = apps.get_model('users', 'User')
    default_password = make_password('12345678')

    for user in User.objects.all():
        user.password = default_password
        user.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='password',
            field=models.CharField(
                default='',
                help_text='Senha armazenada em formato de hash.',
                max_length=128,
                verbose_name='Senha',
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=timezone.now,
                verbose_name='Data de Criação',
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('key', models.CharField(db_index=True, max_length=128, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='auth_tokens',
                        to='users.user',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('token', models.CharField(db_index=True, max_length=128, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('used', models.BooleanField(default=False)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='password_reset_tokens',
                        to='users.user',
                    ),
                ),
            ],
        ),
        migrations.RunPython(set_default_passwords, migrations.RunPython.noop),
    ]