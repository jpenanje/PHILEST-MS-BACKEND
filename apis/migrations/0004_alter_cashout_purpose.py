# Generated by Django 4.2.1 on 2023-05-24 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_cashoutpurpose_remove_purpose_paymentpurpose'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashout',
            name='purpose',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.cashoutpurpose'),
        ),
    ]
