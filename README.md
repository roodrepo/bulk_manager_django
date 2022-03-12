Bulk Manager Django
==========

### *Easier management of the bulk create/update/delete for Django*

Bulk Manager is a plugin for Django to facilitate the bulk features of database operations.

## Features

- Easy to use
- Performance optimization

## Advantages

- Highly flexible
- Lightweight
- Open-source
- Real use cases
- Support & documentation

## Authors

- Rudy Fernandez

## Install
The easiest way to install default_mutable using pip:
`pip install bulk-manager-django`

### Methods

| Attribute | Description |
|:-:|:-|
| `prepareCreate`  | *Add the object to the list*  |
| `create`  | *Bulk create all the objects in the create list* |
| `set`  | *Change an object value* |
| `getValueFromMemory`  | *Access a specific value from an object if previously set* |
| `update`  | *Bulk update* |
| `prepareDelete`  | *Add the object to the list* |
| `delete`  | *Bulk delete* |
| `execute`  | *Perform all actions (create, update and delete) at once* |

#### prepareCreate

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `obj` | Model or list of Models |  | *Model or list of Models to update* |

#### create

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `listObj` | list | [] | *List of strings of all Models to create. If empty, create all pending records* |

#### set

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `obj` | Model |  | *Object to update* |
| `attr` | list or str |  | *'grandfather.father.attr' or ['grandfather', 'father', 'attr']* |
| `value` | Any |  | *Value to set* |

#### getValueFromMemory

| `obj` | Model |  | *Object to get the value from* |
| `attr` | str |  | *Attribute of the object* |
| `default_value` | Any |  | *Default value to return if not in memory* |
For every value updated with the method 'set' is stored in memory. 'getValueFromMemory' checks if the value has previously been updated.

#### update

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `listObj` | list | [] | *List of strings of all Models to update. If empty, create all pending records* |

#### prepareDelete

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `obj` | Model |  | *Record to delete* |

#### delete

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `listObj` | list | [] | *List of strings of all Models to delete. If empty, delete all pending records. Deletion occurs in the same order of the list* |

#### execute

| Argument | Type | Default | Description |
|:-:|:-:|:-:|:-|
| `create_order` | list | [] | *List of strings of all Models to delete. If empty, create all pending records. Creation occurs in the same order of the list* |
| `delete_order` | list | [] | *List of strings of all Models to delete. If empty, delete all pending records. Delation occurs in the same order of the list* |

### [Examples](https://github.com/roodrepo/bulk_manager_django/tree/v0-dev/examples)

```python
from bulk_manager_django.BulkManager import BulkManager
BM = BulkManager()

BM.prepareCreate([
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
])

BM.create() # or BM.execute()

for record in DemoTable.objects.filter(insert_type = 'bulk-manager'):
      BM.set(record, 'description', 'updated description')
      
      BM.set(record, 'platform_name', 'updated platform_name')
      
      BM.set(record, 'is_enabled', randomBool())
      
BM.update() # or BM.execute()

for record in DemoTable.objects.filter(insert_type = 'bulk-manager'):
      BM.prepareDelete(record)
      
   

BM.delete(['DemoTable']) # or BM.delete() or BM.execute() or BM.execute(delete_order= ['DemoTable'])

```