from myapp.models import DemoTable, DemoSubTable, DemoUnrelatedTable
import random
import string

import sys
sys.path.append('/Users/rudy/Documents/Python/packages')
from bulk_manager_django.bulk_manager_django.BulkManager import BulkManager

def randomStatus():
	status = [
		'failed',
		'success',
	]
	return status[random.randint(0, len(status) -1 )]

def randomBool():
	return bool(random.getrandbits(1))

def randomString():
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(10))

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
	
	sub_list_to_insert = []
	unrelated_sub_list_to_insert = []
	
	for idx, main_obj in enumerate(list_to_insert, 1):
		main_obj.save()
		sub_list_to_insert.append(
			DemoSubTable(
				parent          = main_obj,
				sub_name        = f'built-in sub create{idx}-1',
				status          = randomStatus(),
				current_amount  = random.randint(0, 100),
			)
		)
		
		sub_list_to_insert.append(
			DemoSubTable(
				parent          = main_obj,
				sub_name        = f'built-in sub create{idx}-2',
				status          = randomStatus(),
				current_amount  = random.randint(0, 100),
			)
		)
		
		
		
		
		unrelated_sub_list_to_insert.append(
			DemoUnrelatedTable(
				unrelated_name  = randomString(),
				status          = randomStatus(),
			)
		)
		
		unrelated_sub_list_to_insert.append(
			DemoUnrelatedTable(
				unrelated_name  = randomString(),
				status          = randomStatus(),
			)
		)
		
	
	DemoSubTable.objects.bulk_create(sub_list_to_insert)
	DemoUnrelatedTable.objects.bulk_create(unrelated_sub_list_to_insert)
	
	
	# -------------------------------------------------------------------------
	
	list_update_main        = []
	list_update_sub         = []
	memory_total_amount     = {}
	list_delete_sub         = []
	
	for record in DemoSubTable.objects.select_related('parent').filter(parent__insert_type= 'built-in'):
		if record.status == 'success':
			record.status = 'complete'
			
			if record.parent_id not in memory_total_amount:
				memory_total_amount[record.parent_id] = 0
				
			memory_total_amount[record.parent_id]   += record.current_amount
			record.parent.total_amount              = memory_total_amount[record.parent_id]
			
			list_update_main.append(record.parent)
			list_update_sub.append(record)
		
		else:
			list_delete_sub.append(record.id)
	
	print()
	print(f'{"":4}', '**** Update query ****')
	
	DemoTable.objects.bulk_update(list_update_main, ['total_amount'])
	DemoSubTable.objects.bulk_update(list_update_sub, ['status'])
	
	print()
	print(f'{"":4}', '**** Delete query ****')
	
	DemoSubTable.objects.filter(id__in= list_delete_sub).delete()
	
	
	# -------------------------------------------------------------------------
	
	
	print()
	print()
	print()
	print(f'{"":4}', '#### BULK MANAGER ####')
	
	BM = BulkManager()
	
	list_to_insert = [
		DemoTable(
			name        = 'bulk-manager create1',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		),
		DemoTable(
			name        = 'bulk-manager create2',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		),
		DemoTable(
			name        = 'bulk-manager create3',
			is_enabled  = True,
			insert_type = 'bulk-manager',
		)
	]
	
	
	for idx, main_obj in enumerate(list_to_insert, 1):
		
		main_obj.save()
		BM.prepareCreate([
			DemoSubTable(
				parent          = main_obj,
				sub_name        = f'bulk-manager sub create{idx}-1',
				status          = randomStatus(),
				current_amount  = random.randint(0, 100),
			),
			DemoSubTable(
				parent          = main_obj,
				sub_name        = f'bulk-manager sub create{idx}-2',
				status          = randomStatus(),
				current_amount  = random.randint(0, 100),
			)
		])
		
		
		
		BM.prepareCreate([
			DemoUnrelatedTable(
				unrelated_name  = randomString(),
				status          = randomStatus(),
			),
			DemoUnrelatedTable(
				unrelated_name  = randomString(),
				status          = randomStatus(),
			)
		])
		
		
	BM.create()
	
	
	# -------------------------------------------------------------------------
	
	
	for record in DemoSubTable.objects.select_related('parent').filter(parent__insert_type= 'bulk-manager'):
		if record.status == 'success':
			BM.set(record, 'status', 'complete')
			BM.set(record.parent, 'total_amount', BM.getValueFromMemory(record.parent, 'total_amount', default_value= 0) + record.current_amount)
		
		else:
			BM.prepareDelete(record)
	
	print()
	print(f'{"":4}', '**** Update & delete query ****')
	
	BM.execute()
