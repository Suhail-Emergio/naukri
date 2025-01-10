#################################  D A T A  O N  P R O F I L E  C O M P L E T E D  B Y  U S E R  #################################
from seeker.details.models import Personal, Employment, Qualification
from django.db import models

async def completion_data(user):
    empty_models = []
    models_with_empty_fields = {}
    profile_completion_percentage = 0
    models_to_check = {'Personal': Personal, 'Employment': Employment, 'Qualification': Qualification}
    total_fields = 0
    empty_fields_count = 0
    for model_name, model_class in models_to_check.items():
        if model_class == Personal:
            instance = await model_class.objects.aget(user=user)
            instances = [instance]
        else:
            instances = [i async for i in model_class.objects.filter(user=user)]
        if not instances:
            empty_models.append(model_name)
            continue
        empty_fields = set()
        for instance in instances:
            for field in model_class._meta.fields:
                if field.name in ['id', 'user']:
                    continue
                total_fields += 1
                value = getattr(instance, field.name)
                is_empty = False
                if isinstance(field, models.FileField) or isinstance(field, models.ImageField):
                    is_empty = not bool(value)
                elif isinstance(field, models.JSONField):
                    is_empty = value is None or value == {} or value == []
                elif isinstance(field, models.CharField):
                    is_empty = value is None or value.strip() == ''
                else:
                    is_empty = value is None
                if is_empty:
                    empty_fields.add(field.name)
                    empty_fields_count += 1
            if empty_fields:
                models_with_empty_fields[model_name] = list(empty_fields)
    profile_completion_percentage += ((total_fields - empty_fields_count) / total_fields) * 100 if total_fields > 0 else 0
    return profile_completion_percentage, models_with_empty_fields, empty_models 