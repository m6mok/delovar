from django.contrib import admin
from .models import Case


class CaseAdmin(admin.ModelAdmin):
    list_display = ('formatted_receipt', 'formatted_statement', 'formatted_debt_statement', 'formatted_egrn')
    list_filter = ('created_at',)

    def formatted_receipt(self, obj):
        return self._format_file_field(obj.receipt)

    def formatted_statement(self, obj):
        return self._format_file_field(obj.statement)

    def formatted_debt_statement(self, obj):
        return self._format_file_field(obj.debt_statement)

    def formatted_egrn(self, obj):
        return self._format_file_field(obj.egrn)

    formatted_receipt.short_description = 'Квитанция об уплате госпошлины'
    formatted_statement.short_description = 'Заявление'
    formatted_debt_statement.short_description = 'Расчеты по задолженности'
    formatted_egrn.short_description = 'Выписки из ЕГРН'

    def _format_file_field(self, field):
        if field:
            return 'File'
        return 'No file'

    _format_file_field.allow_tags = True


admin.site.register(Case, CaseAdmin)
