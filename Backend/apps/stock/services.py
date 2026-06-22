from django.db import transaction
from apps.logs.services import create_stock_log
from django.core.exceptions import ValidationError
from apps.stock.models import Stock


@transaction.atomic
def stock_in(item, warehouse, user, quantity=1, note=""):
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if item.organization_id != warehouse.organization_id:
        raise ValidationError("Item and warehouse must belong to the same organization.")

    stock_obj, created = Stock.objects.get_or_create(
        organization=item.organization,
        item=item,
        warehouse=warehouse,
        defaults={"quantity": 0}
    )

    stock_obj.quantity += quantity
    stock_obj.save(update_fields=["quantity"])

    create_stock_log(
        organization=item.organization,
        item=item,
        quantity=quantity,
        action="IN",
        performed_by=user,
        note=note,
        sku=item.sku  
    )

    return stock_obj


@transaction.atomic
def stock_out(*, item, warehouse, quantity, user, note=None):
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if item.organization_id != warehouse.organization_id:
        raise ValidationError("Item and warehouse must belong to the same organization.")

    stock_obj = Stock.objects.get(
        organization=item.organization,
        item=item,
        warehouse=warehouse,
    )

    if stock_obj.quantity < quantity:
        raise ValidationError("Insufficient stock.")

    stock_obj.quantity -= quantity
    stock_obj.save(update_fields=["quantity"])

    create_stock_log(
        organization=item.organization,
        item=item,
        quantity=quantity,
        action="OUT",
        performed_by=user,
        note=note or "Stock out via API",
        sku=item.sku   
    )

    return stock_obj
