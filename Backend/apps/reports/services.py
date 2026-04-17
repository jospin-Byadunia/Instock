from django.apps import apps
import csv
from io import StringIO

def export_table(model_name, app_name, start_date=None, end_date=None):
    """
    Export a table to CSV format.
    :param model_name: Name of the model (string)
    :param app_name: Name of the app where the model resides (string)
    :param start_date: Optional start date (for filtering logs)
    :param end_date: Optional end date (for filtering logs)
    :return: CSV data as a string
    """
    model = apps.get_model(app_name, model_name)
    queryset = model.objects.all()

    if model_name.lower() == "stocklog" and start_date and end_date:
        queryset = queryset.filter(created_at__date__range=[start_date, end_date])

    data = []
    for obj in queryset:
        row = {}
        for field in obj._meta.get_fields():
            if field.is_relation and hasattr(getattr(obj, field.name, None), '__str__'):
                row[field.name] = str(getattr(obj, field.name, ''))
            elif not field.is_relation:
                row[field.name] = getattr(obj, field.name, '')
        data.append(row)

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    return output.getvalue()
