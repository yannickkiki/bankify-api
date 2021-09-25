from django.db import migrations


def create_super_user(apps, schema_editor):
    User = apps.get_model('user', 'User')

    User.objects.create_user(username='bankify', password='bankify')
    User.objects.create_user(username='bankai', password='bankai')


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_super_user)
    ]
