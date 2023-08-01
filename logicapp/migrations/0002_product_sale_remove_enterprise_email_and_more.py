# Generated by Django 4.2.2 on 2023-08-01 16:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('logicapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('name', models.CharField(default='-----', max_length=1000)),
                ('picture', models.ImageField(null=True, upload_to='images/')),
                ('inventory', models.IntegerField(null=True)),
                ('inventory_minimal', models.IntegerField(default=0, null=True)),
                ('price', models.FloatField(default=0, null=True)),
                ('id', models.IntegerField(db_index=True, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('data', models.DateTimeField()),
                ('quantity', models.IntegerField(null=True)),
                ('uuid', models.UUIDField(default=uuid.UUID('60960040-6a28-4052-9e0f-f4290b0e4aba'), primary_key=True, serialize=False, unique=True)),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.RemoveField(
            model_name='enterprise',
            name='email',
        ),
        migrations.AddField(
            model_name='area',
            name='add_employee',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='add_product',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='add_sales',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='area_add',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='control_employee',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='control_sales',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='enterprise',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='area', to='logicapp.enterprise'),
        ),
        migrations.AddField(
            model_name='area',
            name='inventory_control',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='sales_analysis',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='area',
            name='settings',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='enterprise',
            field=models.ManyToManyField(blank=True, to='logicapp.enterprise'),
        ),
        migrations.AddField(
            model_name='enterprise',
            name='enterprise',
            field=models.CharField(max_length=14, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='cpf',
            field=models.CharField(max_length=14, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='picture',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='area',
            name='id',
            field=models.IntegerField(db_index=True, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='enterprise',
            name='picture',
            field=models.ImageField(null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='enterprise',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('991f5815-9f50-4e9a-a1d2-45859fa95159'), unique=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='area',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='area', to='logicapp.area'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='enterprise',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee', to='logicapp.enterprise'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('163cfc42-d652-45cc-af1b-bfc4162dc1ed'), unique=True),
        ),
        migrations.CreateModel(
            name='Text_Message',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.UUID('3e3d96de-a4bc-4fa0-bfa0-f6354ff4d05d'), primary_key=True, serialize=False, unique=True)),
                ('data', models.DateTimeField(null=True)),
                ('title', models.CharField(default='', max_length=100000, null=True)),
                ('text', models.CharField(default='', max_length=100000, null=True)),
                ('enterprise', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Enterprise_Messages', to='logicapp.enterprise')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCar',
            fields=[
                ('uuid', models.UUIDField(default=uuid.UUID('32a922b4-aecb-4907-9b69-bbe85f7599d1'), primary_key=True, serialize=False, unique=True)),
                ('products', models.CharField(default='-----------', max_length=1000)),
                ('data', models.DateTimeField(null=True)),
                ('enterprise', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='marketconfirmenterprise', to='logicapp.enterprise')),
                ('profile', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profileconfirm', to='logicapp.profile')),
                ('sales', models.ManyToManyField(to='logicapp.sale')),
            ],
        ),
        migrations.CreateModel(
            name='Sales_Made',
            fields=[
                ('uuid', models.UUIDField(db_index=True, default=uuid.UUID('a2e52664-69fe-424e-91af-9513b2452925'), primary_key=True, serialize=False, unique=True)),
                ('data', models.DateTimeField(null=True)),
                ('quantity', models.CharField(default='', max_length=1000000, null=True)),
                ('total', models.FloatField(default=0, null=True)),
                ('payment_method', models.CharField(choices=[('Credit Cart', 'Credit Cart'), ('Debit Car', 'Debit Car'), ('Money', 'Money')], default='', max_length=1000, null=True)),
                ('enterprise', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Sales_employees', to='logicapp.enterprise')),
                ('product', models.ManyToManyField(to='logicapp.product')),
                ('profile', models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Sales', to='logicapp.profile')),
            ],
        ),
        migrations.AddField(
            model_name='sale',
            name='enterprise',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale', to='logicapp.enterprise'),
        ),
        migrations.AddField(
            model_name='sale',
            name='product',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='logicapp.product'),
        ),
        migrations.AddField(
            model_name='product',
            name='enterprise',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product', to='logicapp.enterprise'),
        ),
    ]
