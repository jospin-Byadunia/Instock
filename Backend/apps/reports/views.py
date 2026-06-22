from rest_framework.views import APIView
from django.http import HttpResponse
from apps.reports.services import export_table
from apps.accounts.authentication import CookieJWTAuthentication
from apps.auth_app.permissions import IsAdmin


def export_organization(request):
    if request.user.is_superuser:
        return None
    return request.user.organization

class StockLogExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        csv_data = export_table(
            'StockLog',
            'logs',
            start_date=start_date,
            end_date=end_date,
            organization=export_organization(request),
        )

        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stocklog_report.csv"'
        return response

class WarehouseExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table(
            'Warehouse',
            'stock',
            organization=export_organization(request),
        )
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="warehouse_report.csv"'
        return response

class StockExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table(
            'Stock',
            app_name='stock',
            organization=export_organization(request),
        )
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
        return response

class ItemExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table(
            'Item',
            app_name='items',
            organization=export_organization(request),
        )
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="item_report.csv"'
        return response

class CategoryExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table(
            'Category',
            app_name='items',
            organization=export_organization(request),
        )
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="category_report.csv"'
        return response

class UserExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table(
            'CustomUser',
            app_name='accounts',
            organization=export_organization(request),
        )
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_report.csv"'
        return response
