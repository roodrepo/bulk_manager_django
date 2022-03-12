from myapp.models import DemoTable, DemoSubTable, DemoUnrelatedTable
import random
import string

import sys
sys.path.append('/Users/rudy/Documents/Python/packages')
from bulk_manager_django.bulk_manager_django.BulkManager import BulkManager


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
			name        = None,
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
	
	'''
		Nothing is saved in the database
	'''
	try:
		DemoTable.objects.bulk_create(list_to_insert)   # Not working because NOT NULL constraint failed: myapp_demotable.name
	except Exception as e:
		print(e)
		
		
	
	# -------------------------------------------------------------------------
	
	print()
	print()
	print()
	print(f'{"":4}', '#### BULK MANAGER ####')
	
	
	BM = BulkManager()
	
	BM.prepareCreate([
		DemoTable(
			name        = None,
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
	])
	
	'''
		Even though there is an error, all the other records are still saved in the database
	'''
	try:
		BM.create()
	except Exception as e:
		print(e)
	