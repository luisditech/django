# Generated by Django 4.2.20 on 2025-06-10 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('connections', '0005_connection_is_active'),
        ('works', '0002_remove_work_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='work',
            name='connection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='connections.connection'),
        ),
    ]
