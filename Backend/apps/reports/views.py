from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse
from apps.reports.services import export_table
from apps.accounts.authentication import CookieJWTAuthentication
from rest_framework.response import Response
from apps.auth_app.permissions import IsAdmin

class StockLogExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        csv_data = export_table('StockLog', 'logs', start_date=start_date, end_date=end_date)

        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stocklog_report.csv"'
        return response

class WarehouseExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table('Warehouse', 'stock')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="warehouse_report.csv"'
        return response

class StockExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table('Stock', app_name='stock')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="stock_report.csv"'
        return response

class ItemExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table('Item', app_name='items')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="item_report.csv"'
        return response

class CategoryExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        csv_data = export_table('Category', app_name='items')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="category_report.csv"'
        return response

class UserExportView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAdmin]

    def get(self, request):
        csv_data = export_table('CustomUser', app_name='accounts')
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user_report.csv"'
        return response
