from django.contrib import admin
from seeker.details.models import *
from seeker.seeker_actions.models import BlockedCompanies

admin.site.register(Personal)
admin.site.register(Employment)
admin.site.register(Qualification)
admin.site.register(Preference)
admin.site.register(NotificationPreference)
admin.site.register(SearchApps)
admin.site.register(BlockedCompanies)