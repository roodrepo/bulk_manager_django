from myapp.models import DemoTable, DemoSubTable, DemoUnrelatedTable
import random

import sys
# sys.path.append('/Users/rudy/Documents/Python/packages')
from bulk_manager_django.BulkManager import BulkManager

def randomBool():
	return bool(random.getrandbits(1))

def run():
	# Reset the table
	DemoSubTable.objects.all().delete()
	DemoTable.objects.all().delete()
	DemoUnrelatedTable.objects.all().delete()
	
	print()
	print('--------- BEGIN DEMO ---------')
	print()
	print(f'{"":4}', '#### BUILT-IN ####')
	
	list_to_insert = [
		DemoTable(
			name        = 'built-in create1',
			is_enabled  = True,
			insert_type = 'built-in',
		),
		DemoTable(
			name        = 'built-in create2',
			is_enabled  = True,
			insert_type = 'built-in',
		),
		DemoTable(
			name        = 'built-in create3',
			is_enabled  = True,
			insert_type = 'built-in',
		)
	]
	
	print()
	print(f'{"":4}', '**** Create query ****')
	DemoTable.objects.bulk_create(list_to_insert)   # One query to insert all
	
	# -------------------------------------------------------------------------
	print()
	print(f'{"":4}', '**** Update query ****')
	
	list_update = []
	list_field_update = []
	for record in DemoTable.objects.filter(insert_type = 'built-in'):
		if randomBool() == True:
			record.description = 'updated description'
			list_field_update.append('description')
			
		if randomBool() == True:
			record.platform_name = 'updated platform_name'
			list_field_update.append('platform_name')
			
		if randomBool() == True:
			record.is_enabled = randomBool()
			list_field_update.append('is_enabled')
		
		list_update.append(record)
	
	
	DemoTable.objects.bulk_update(list_update, list(set(list_field_update)))
	
	
	# -------------------------------------------------------------------------
	print()
	print(f'{"":4}', '**** Delete query ****')
	
	list_delete_id = []
	for record in DemoTable.objects.filter(insert_type = 'built-in'):
		if randomBool() == True:
			list_delete_id.append(record.id)
	
	DemoTable.objects.filter(id__in= list_delete_id).delete()
	
	
	
	
	
	
	
	
	
	
	# -------------------------------------------------------------------------
	
	print()
	print()
	print()
	print(f'{"":4}', '#### BULK MANAGER ####')
		
	BM = BulkManager()
	
	BM.prepareCreate(
		DemoTable(
			name        = 'bulk-manager create1',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		)
	)
	BM.prepareCreate(
		DemoTable(
			name        = 'bulk-manager create2',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		)
	)
	BM.prepareCreate(
		DemoTable(
			name        = 'bulk-manager create3',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		)
	)
	
	print()
	print(f'{"":4}', '**** Create query ****')
	
	BM.create()
	
	print()
	print(f'{"":4}', '**** Update query ****')
	
	for record in DemoTable.objects.filter(insert_type = 'bulk-manager'):
		if randomBool() == True:
			BM.set(record, 'description', 'updated description')
			
		if randomBool() == True:
			BM.set(record, 'platform_name', 'updated platform_name')
			
		if randomBool() == True:
			BM.set(record, 'is_enabled', randomBool())
			
	BM.update()
	
	# -------------------------------------------------------------------------
	print()
	print(f'{"":4}', '**** Delete query ****')
	
	for record in DemoTable.objects.filter(insert_type = 'bulk-manager'):
		if randomBool() == True:
			BM.prepareDelete(record)
			
		
	
	BM.delete()
	
	
