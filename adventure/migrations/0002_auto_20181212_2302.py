# Generated by Django 2.1.1 on 2018-12-13 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adventure', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='DEFAULT TITLE', max_length=50)),
                ('description', models.CharField(default='DEFAULT DESCRIPTION', max_length=500)),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='items',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='adventure.Item')),
                ('attack_power', models.IntegerField(default=0)),
                ('equippable', models.BooleanField(default=True)),
            ],
            bases=('adventure.item',),
        ),
    ]