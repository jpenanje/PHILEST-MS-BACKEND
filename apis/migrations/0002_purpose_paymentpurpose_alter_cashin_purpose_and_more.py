# Generated by Django 4.2.1 on 2023-05-24 12:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purpose',
            name='paymentPurpose',
            field=models.CharField(default='cashIn', max_length=256),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='cashin',
            name='purpose',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.purpose'),
        ),
        migrations.AlterField(
            model_name='student',
            name='full_name',
            field=models.TextField(max_length=1000, unique=True),
        ),
    ]