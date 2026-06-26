from django.db import migrations, models


def set_demo_emails(apps, schema_editor):
    User = apps.get_model('users', 'User')

    demo_emails = {
        'admin': 'admin@kanban.com',
        'usuario': 'usuario@kanban.com',
        'admin_teste': 'admin@kanban.com',
    }

    for name, email in demo_emails.items():
        User.objects.filter(name=name).update(email=email)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auth_tokens_and_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(
                blank=True,
                help_text='Email do usuário, usado para recuperação de senha.',
                max_length=254,
                null=True,
                unique=True,
                verbose_name='Email',
            ),
        ),
        migrations.RunPython(set_demo_emails, migrations.RunPython.noop),
    ]