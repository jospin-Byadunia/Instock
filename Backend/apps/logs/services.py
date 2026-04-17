from .models import StockLog

def create_stock_log(*, item, action,  performed_by=None, note=None, quantity=None, sku=None):
    StockLog.objects.create(
        item=item,
        quantity=quantity,
        sku=item.sku,
        action=action,
        performed_by= performed_by,
        note=note
    )
