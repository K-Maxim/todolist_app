# Generated by Django 4.1.2 on 2022-11-15 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0007_alter_goalcategory_board'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goalcategory',
            name='board',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='board', to='goals.board', verbose_name='Доска'),
        ),
    ]
