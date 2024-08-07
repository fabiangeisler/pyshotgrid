## v2.0.2 (2024-05-04)

### Fix

- **new_site**: allow subclasses of shotgun_api3.Shotgun as first parameter
- **SGEntity._version**: do not error on SG Versions with empty "entity" field

## v2.0.1 (2024-05-04)

### BREAKING CHANGE

- This results in the drop of Python 3.8 as it is not supported by the shotgun-api3.

## v1.1.0 (2023-11-04)

### Feat

- **PyPI**: Use shotgun-api3 from PyPI

### Fix

- **new_site**: support tk-core and shotgun_api3 environments

## v1.0.1 (2023-09-06)

### Fix

- **SGEntity**: do not cast url fields to Attachment SGEntities

### Perf

- **sg_default_entities**: Improve performance for ".name" property

## v1.0.0 (2023-08-28)

## v0.15.0 (2023-08-27)

### Feat

- **Field**: Make Field inherit FieldSchema
- **SGEntity**: Add thumbnail and filmstrip properties

## v0.14.0 (2023-07-26)

### Feat

- **SGPublishedFile**: Rename "get_latest_publish" to "get_latest"
- **default-entities**: add "versions" function to all relevant entities
- **core**: Remove "additional_sg_filter" argument from various functions
- **Default-entities**: Add "tasks" function to various entities
- **SGEntity**: Add DEFAULT_SG_ENTITY_TYPE var to make entity_type optional

### Fix

- **Field**: remove all field property setter methods
- **SGEntity**: fix pipeline_step argument in _version function
- **SGProject.people**: fix shotgrid query
- **SGSite.pipeline_configuration**: fix various issues with the function

## v0.13.0 (2023-04-29)

### Feat

- **SGPublishedFile**: add methods to query publish versions

## v0.12.0 (2023-04-13)

### Feat

- **SGSite**: Make SGSite comparable
- **all**: Refactor pysg for maximum mypy compilance

### Fix

- **SGSite**: Fix comparison against other types

## v0.11.0 (2023-03-07)

### Feat

- **SGEntity**: rename "display_name" to "entity_display_name"
- **SGEntity**: add "name" property

## v0.10.0 (2023-01-18)

### Feat

- **SGSite**: add entity_field_schemas function
- **SGEntity**: add display_name property

## v0.9.1 (2023-01-01)

### Fix

- **Release**: GitHub action

## v0.9.0 (2023-01-01)

### Feat

- **SGEntity**: comparebility for SGEntity instances
- **fields**: Split Field schema to its own class

## v0.8.0 (2022-11-28)

### Feat

- **Field**: Add valid_types property to Field class

### Fix

- **SGSite**: "find_one" function return Field instead of SGEntity
- **SGEntity**: fix converion of project_enities for "filed" and "all_field_values"
- **Field**: convert project entities before passing them to sg schema
- **core**: add missing mockgun import
- **SGAsset**: Incorrect entity type

## v0.7.1 (2022-08-08)

## v0.7.0 (2022-08-08)
