from django.db import models

enum_insert_type = [
	('built-in', 'built-in'),
	('bulk-manager', 'bulk-manager'),
]

class DemoTable(models.Model):
	name            = models.CharField(max_length=50, null=False, blank=False, unique= True)
	description     = models.CharField(max_length=50, null=True)
	platform_name   = models.CharField(max_length=50, null=True)
	is_enabled      = models.BooleanField(default=True)
	insert_type     = models.CharField(max_length=50, null=False, blank=False, choices= enum_insert_type)
	total_amount    = models.FloatField(blank=True, null=True, default=0)
	
	
class DemoSubTable(models.Model):
	parent          = models.ForeignKey(DemoTable, null=False, blank=False, on_delete=models.PROTECT)
	sub_name        = models.CharField(max_length=50, null=True)
	status          = models.CharField(max_length=50, null=True)
	current_amount  = models.FloatField(blank=True, null=True, default=0)
	
	
	
class DemoUnrelatedTable(models.Model):
	unrelated_name  = models.CharField(max_length=50, null=True)
	status          = models.CharField(max_length=50, null=True)
	
	