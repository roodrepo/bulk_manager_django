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
	
	
	def delete(self, listToDelete : list = []) -> None:
		'''
		Performing delete according to the list passed
		
		:param listToDelete:
		:return:
		'''
		
		# If the list is empty, we delete everything in the default order (FIFO)
		if len(listToDelete) == 0:
			listToDelete = self._table_order_delete
		else:
			listToDelete = self._getTablesNameFromList(listToDelete)
			self._setDeleteOrderFromTablesName(listToDelete)
			
		query_update_set_null = ''
		query_delete = ''
		
		# Looping all the tables from the ordered list
		for _table_name in self._table_order_delete:
			# Checking if table is in the current list passed to delete
			if _table_name in listToDelete:
				if _table_name in self._deletes:
					query_delete += f'DELETE FROM {_table_name} WHERE {self._deletes[_table_name]["pk_field"]} IN ({", ".join(self._deletes[_table_name]["ids"])});'
					del self._deletes[_table_name]
				else:
					raise Exception(f'{_table_name} not found')
				
		final_query = query_update_set_null + query_delete
		if final_query != '':
			with connection.cursor() as cursor:
				cursor.execute(final_query)
	
	
	def prepareDelete(self, obj: TypeClass) -> None:
		'''
		Kepping in memory all the parameters to perform a bulk delete later on
		
		:param obj: django object to delete or a QuerySet to delete
		:return:
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
		
	def getValueFromMemory(self, obj: TypeClass, key: str, default_value: Union[str, int, float, bool, None] = None) -> Union[str, int, float, bool, None]:
		'''
		
		
		:param obj:
		:param key:
		:param default_value:
		:return:
		'''
		if default_value == None and isinstance(getattr(obj, key), (int, float)) == True:
			default_value = 0
			
		pk_value = getattr(obj, obj._meta.pk.name)
		
		class_name = obj.__class__.__name__
		if class_name in self._objects and pk_value in self._objects[class_name] and hasattr(self._objects[class_name][pk_value], key):
			return getattr(self._objects[class_name][pk_value], key)
		
		return default_value
	
	
	def set(self, obj: TypeClass, attrs: Union[str, list], value: Any) -> None:
		if type(attrs) == str:
			attrs = attrs.split('.')
			
		up_obj, is_updated, objclass = self._deepSetAttr(obj, attrs, value)
		
		classname = objclass.__name__
		cur_field = attrs[-1]
		
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
				setattr(self._objects[classname][pk_value], attrs[0], value)
				
	@defaultMutable
	def update(self, listObj: list = []) -> None:
		if len(listObj) == 0:
			listObj = list(self._fields.keys())
			
		for obj in listObj:
			if obj in self._objects:
				_listUpdateObj = list(self._objects[obj].values())
				try:
					self._classes[obj]._objects.bulk_update(_listUpdateObj, self._fields[obj])
				except Exception as e:
					# In case the bulk threw an error, we update the objects one by one to avoid data loss
					for __objToUpdate in _listUpdateObj:
						try:
							__objToUpdate.save()
						except Exception as e:
							print('Error bulk update: ' + e)
							
							
							
				del self._fields[obj]
				del self._objects[obj]
				if obj not in self._creates:
					del self._classes[obj]
			
			
	def prepareCreate(self, obj: TypeClass) -> None:
		classname = obj.__class__.__name__
		if classname not in self._creates:
			self._creates[classname] = []
		
		self._classes[classname] = obj.__class__
		self._creates[classname].append(obj)
	
	@defaultMutable
	def create(self, listObj: list = []) -> None:
		if len(listObj) == 0:
			listObj = list(self._creates.keys())
			
			
		for obj in listObj:
			try:
				self._classes[obj]._objects.bulk_create(self._creates[obj])
			except Exception as e:
				# In case the bulk threw an error, we update the objects one by one to avoid data loss
				for __objToCreate in self._creates[obj]:
					try:
						__objToCreate.save()
					except Exception as e:
						print('Error bulk create: ' + e)
						
						
						
			del self._creates[obj]
			if obj not in self._fields:
				del self._classes[obj]







	# 	Setting the order of deletion to avoid relationship constraint issues
	@defaultMutable
	def _setDeleteOrderFromObjName(self, _list: list = []) -> None:
		current_list = self._table_order_delete
		self._table_order_delete = []
		for _obj in _list:
			_table_name = self._mapping_obj_table_name[_obj]
			self._table_order_delete.append(_table_name)
			current_list.remove(_table_name)
			
		self._table_order_delete += current_list
	
	# 	Setting the order of deletion to avoid relationship constraint issues
	@defaultMutable
	def _setDeleteOrderFromTablesName(self, _list: list = []) -> None:
		current_list = self._table_order_delete
		self._table_order_delete = []
		for _table_name in _list:
			self._table_order_delete.append(_table_name)
			current_list.remove(_table_name)
			
		self._table_order_delete += current_list
	
	
	
	
	# 	returning the list with the tables name in case there is the Model name in the list
	def _getTablesNameFromList(self, _list: list) -> list:
		response = []
		for item in _list:
			if item in self._mapping_obj_table_name:
				response.append(self._mapping_obj_table_name[item])
			else:
				response.append(item)
				
		return response
	
	
	def _deepSetAttr(self, obj: TypeClass, attrs: Union[str, list], value: Any) -> Tuple[TypeClass, bool, TypeClass]:
		if type(attrs) == str:
			attrs = attrs.split('.')
		
		cur_obj = obj
		objclass = None
		is_updated = False
		
		for _attr in attrs:
			if _attr == attrs[-1]:
				objclass = cur_obj.__class__
				
				cur_value = getattr(cur_obj, _attr)
				if cur_value != value:
					setattr(cur_obj, _attr, value)
					is_updated = True
			else:
				cur_obj = getattr(cur_obj, _attr)
		
		
		return cur_obj, is_updated, objclass