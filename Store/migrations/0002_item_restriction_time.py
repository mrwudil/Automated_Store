# Generated by Django 3.1 on 2021-10-29 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='restriction_time',
            field=models.CharField(choices=[('Day', 'Day'), ('Week', 'Week'), ('Month', 'Month'), ('Half A Year', 'Half'), ('Year', 'Year')], default='Day', max_length=20),
            preserve_default=False,
        ),
    ]