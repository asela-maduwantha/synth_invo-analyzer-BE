from django.urls import path
from . import views

urlpatterns = [
    path('organization/signup/', views.organization_signup, name='organization_signup'),
    path('organization/login/', views.organization_login, name='organization_login'),
    path('supplier/login/', views.supplier_login, name='supplier_login'),
    path('systemadmin/signup/', views.system_admin_signup, name='system_admin_signup'),
    path('systemadmin/login/', views.system_admin_login, name='system_admin_login'),
    path('organization/protected/', views.OrganizationProtectedView, name='protected-organization'),
    path('systemadmin/protected/', views.AdminProtectedView, name='protected-systemadmin'),
    path('supplier/protected/', views.SupplierProtectedView, name='protected-supplier'),
    path('add-supplier/', views.add_supplier, name ='add-supplier'),
    path('register-new-supplier/', views.supplier_register, name='ad-new-supplier'),
    path('verify-otp/', views.verify_otp_view, name='verify-otp'),
    path('resend-otp/', views.resend_otp_view, name = 'resend-otp'),
    path('send-otp/', views.send_otp_view, name = 'resend-otp'),
    path('get-organizations-by-supplier/<supplier_id>', views.organizations_by_supplier, name = 'org-supplier'),
    path('get-add-requests-by-supplier/<supplier_id>', views.add_requests_by_supplier_id, name='get-add-requests-by-supplier'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('dismiss-request/<int:request_id>/', views.dismiss_request, name='dismiss_request'),
]
