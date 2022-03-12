from django.db import connection
from django.db.models.query import QuerySet
from typing import Any, Tuple, TypeVar, Union
from default_mutable.DefaultMutable import defaultMutable

TypeClass = TypeVar('TypeClass')

class BulkManager:
	
	_fields                 : dict  = {}
	_objects                : dict  = {}
	_classes                : dict  = {}
	_deletes                : dict  = {}
	_creates                : dict  = {}
	_mapping_obj_table_name : dict  = {}
	_table_order_delete     : list  = []
	
	
	def delete(self, listObj : list = []) -> None:
		'''
			Performing delete according to the list passed
		'''
		
		# If the list is empty, we delete everything in the default order (FIFO)
		if len(listObj) == 0:
			listObj = self._table_order_delete
		else:
			listObj = self._getTablesNameFromList(listObj)
			self._setDeleteOrderFromTablesName(listObj)
			
		query_update_set_null = ''
		query_delete = []
		
		# Looping all the tables from the ordered list
		for _table_name in self._table_order_delete:
			# Checking if table is in the current list passed to delete
			if _table_name in listObj:
				if _table_name in self._deletes:
					query_delete.append(f'DELETE FROM {_table_name} WHERE {self._deletes[_table_name]["pk_field"]} IN ({", ".join(self._deletes[_table_name]["ids"])})')
					del self._deletes[_table_name]
				else:
					raise Exception(f'{_table_name} not found')
				
		final_query = query_update_set_null + ';'.join(query_delete)
		if final_query != '':
			with connection.cursor() as cursor:
				cursor.execute(final_query)
	
	
	def prepareDelete(self, obj: TypeClass) -> None:
		'''
		Kepping in memory all the parameters to perform a bulk delete later on
		
		:param obj: django object to delete or a QuerySet to delete
		'''
		
		if isinstance(obj, QuerySet):
			for record in obj:
				self.prepareDelete(record)
		else:
			
			tablename = obj._meta.db_table
			pk_name = obj._meta.pk.name
			if tablename not in self._deletes:
				self._mapping_obj_table_name[obj.__class__.__name__] = tablename
				self._table_order_delete.append(tablename)
				
				self._deletes[tablename] = {
					'pk_field'  : pk_name,
					'ids'       : [],
				}
				
			self._deletes[tablename]['ids'].append(str(getattr(obj, pk_name)))
		
	
	def getValueFromMemory(self, obj: TypeClass, attr: str, default_value: Union[str, int, float, bool, None] = None) -> Union[str, int, float, bool, None]:
		'''
			Access the value of an object previously updated
		'''
		if default_value == None and isinstance(getattr(obj, attr), (int, float)) == True:
			default_value = 0
			
		pk_value = getattr(obj, obj._meta.pk.name)
		
		class_name = obj.__class__.__name__
		if class_name in self._objects and pk_value in self._objects[class_name] and hasattr(self._objects[class_name][pk_value], attr):
			return getattr(self._objects[class_name][pk_value], attr)
		
		return default_value
	
	
	def set(self, obj: TypeClass, attr: Union[str, list], value: Any) -> None:
		'''
			Set a values to update
		'''
		if type(attr) == str:
			attr = attr.split('.')
			
		up_obj, is_updated, objclass = self._deepSetAttr(obj, attr, value)
		
		classname = objclass.__name__
		cur_field = attr[-1]
		
		if is_updated == True:
			pk_value = getattr(obj, up_obj._meta.pk.name)
			
			if classname not in self._fields:
				self._fields[classname]  = []
				self._objects[classname] = {}
				self._classes[classname] = objclass
				
			if cur_field not in self._fields[classname]:
				self._fields[classname].append(cur_field)
			
			if pk_value not in self._objects[classname]:
				self._objects[classname][pk_value] = up_obj
			else:
				# Only updating the current value
				setattr(self._objects[classname][pk_value], attr[0], value)
				
		
				
	@defaultMutable
	def update(self, listObj: list = []) -> None:
		'''
			Perform bulk update
		'''
		if len(listObj) == 0:
			listObj = list(self._fields.keys())
		
		exception = None
		
		for obj in listObj:
			if obj in self._objects:
				_listUpdateObj = list(self._objects[obj].values())
				try:
					self._classes[obj].objects.bulk_update(_listUpdateObj, self._fields[obj])
				except Exception as e:
					# In case the bulk threw an error, we update the objects one by one to avoid data loss
					for __objToUpdate in _listUpdateObj:
						try:
							__objToUpdate.save()
						except Exception as e:
							exception= f'Error bulk create: {str(e)}'
							
							
							
				del self._fields[obj]
				del self._objects[obj]
				if obj not in self._creates:
					del self._classes[obj]
					
		if exception is not None:
			raise Exception(exception)
			
			
	def prepareCreate(self, obj: Union[TypeClass, list]) -> None:
		'''
			Prepare the list of all objects to create in bulk
		'''
		if isinstance(obj, (list, set)):
			for _obj in obj:
				self._prepareCreateObj(_obj)
				
		else:
			self._prepareCreateObj(obj)
	
	def _prepareCreateObj(self, obj: TypeClass) -> None:
		
		classname = obj.__class__.__name__
		if classname not in self._creates:
			self._creates[classname] = []
		
		self._classes[classname] = obj.__class__
		self._creates[classname].append(obj)
	
	@defaultMutable
	def create(self, listObj: list = []) -> None:
		'''
			Perform bulk create
		'''
		
		if len(listObj) == 0:
			listObj = list(self._creates.keys())
			
		
		exception = None
		for obj in listObj:
			try:
				self._classes[obj].objects.bulk_create(self._creates[obj])
			except Exception as e:
				# In case the bulk threw an error, we update the objects one by one to avoid data loss
				for __objToCreate in self._creates[obj]:
					try:
						__objToCreate.save()
					except Exception as e:
						exception= f'Error bulk create: {str(e)}'
					
						
						
			del self._creates[obj]
			if obj not in self._fields:
				del self._classes[obj]
				
		if exception is not None:
			raise Exception(exception)

	@defaultMutable
	def execute(self, create_order: list= [], delete_order: list= []) -> None:
		'''
			Perform all the pending operations
		'''
		self.create(create_order)
		self.update()
		self.delete(delete_order)
		

	@defaultMutable
	def _setDeleteOrderFromObjName(self, _list: list = []) -> None:
		'''
			Setting the order of deletion to avoid relationship constraint issues
		'''
		current_list = self._table_order_delete
		self._table_order_delete = []
		for _obj in _list:
			_table_name = self._mapping_obj_table_name[_obj]
			self._table_order_delete.append(_table_name)
			current_list.remove(_table_name)
			
		self._table_order_delete += current_list
	
	
	@defaultMutable
	def _setDeleteOrderFromTablesName(self, _list: list = []) -> None:
		'''
			Setting the order of deletion to avoid relationship constraint issues
		'''
		current_list = self._table_order_delete
		self._table_order_delete = []
		for _table_name in _list:
			self._table_order_delete.append(_table_name)
			current_list.remove(_table_name)
			
		self._table_order_delete += current_list
	
	
	
	
	
	def _getTablesNameFromList(self, _list: list) -> list:
		'''
			returning the list with the tables name in case there is the Model name in the list
		'''
		response = []
		for item in _list:
			if item in self._mapping_obj_table_name:
				response.append(self._mapping_obj_table_name[item])
			else:
				response.append(item)
				
		return response
	
	
	def _deepSetAttr(self, obj: TypeClass, attr: Union[str, list], value: Any) -> Tuple[TypeClass, bool, TypeClass]:
		'''
			Update a value from a multi level object
		'''
		if type(attr) == str:
			attr = attr.split('.')
		
		cur_obj = obj
		objclass = None
		is_updated = False
		
		for _attr in attr:
			if _attr == attr[-1]:
				objclass = cur_obj.__class__
				
				cur_value = getattr(cur_obj, _attr)
				if cur_value != value:
					setattr(cur_obj, _attr, value)
					is_updated = True
			else:
				cur_obj = getattr(cur_obj, _attr)
		
		
		return cur_obj, is_updated, objclass