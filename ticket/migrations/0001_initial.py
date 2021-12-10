# Generated by Django 4.0 on 2021-12-10 08:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_user_phone_alter_user_email_alter_user_first_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField()),
                ('open_time', models.DateTimeField(auto_now_add=True)),
                ('close_time', models.DateTimeField(blank=True, null=True)),
                ('contact_preference', models.CharField(choices=[('M', 'Mail'), ('C', 'Call'), ('S', 'Sms'), ('W', 'Whatsapp')], max_length=1)),
                ('agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agent_tickets', to='accounts.user')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lead_tickets', to='accounts.user')),
            ],
        ),
    ]
