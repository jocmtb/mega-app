# Generated by Django 3.2.8 on 2021-12-20 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ARP_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.CharField(max_length=200)),
                ('arp_mac', models.CharField(max_length=200)),
                ('arp_ip', models.CharField(max_length=200)),
                ('arp_intf', models.CharField(max_length=200)),
                ('arp_vlan', models.CharField(max_length=200)),
                ('vlan_name', models.CharField(max_length=200)),
                ('datetime', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Collections',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=200)),
                ('uuid', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=200)),
                ('err_msg', models.CharField(default='na', max_length=200)),
                ('datetime', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Devices',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=200)),
                ('ip_address', models.CharField(max_length=200)),
                ('platform', models.CharField(max_length=200)),
                ('version', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='IGMP_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.CharField(max_length=200)),
                ('mcast_grp', models.CharField(max_length=200)),
                ('mcast_src', models.CharField(max_length=200)),
                ('version', models.CharField(max_length=200)),
                ('reporter_ip', models.CharField(max_length=200)),
                ('intf', models.CharField(max_length=200)),
                ('datetime', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Mcast_flows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.CharField(max_length=200)),
                ('src_mcast', models.CharField(max_length=200)),
                ('mcast_grp', models.CharField(max_length=200)),
                ('in_intf', models.CharField(max_length=200)),
                ('rpf_neighbor', models.CharField(max_length=200)),
                ('flow_status', models.CharField(max_length=200)),
                ('out_intf', models.CharField(max_length=200)),
                ('data_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Script_logs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.CharField(max_length=200)),
                ('script_type', models.CharField(max_length=200)),
                ('file_location', models.CharField(max_length=200)),
                ('data_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
        migrations.CreateModel(
            name='Traffic_interfaces',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host_id', models.CharField(max_length=200)),
                ('interface_id', models.CharField(max_length=200)),
                ('input_rate', models.BigIntegerField()),
                ('output_rate', models.BigIntegerField()),
                ('data_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
