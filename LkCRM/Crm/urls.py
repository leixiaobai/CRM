from django.urls import path,re_path
from Crm import views

urlpatterns = [
    path('allcustomers/list/', views.CustomersList.as_view(), name='allcustomers_list'),
    path('customers/list/', views.CustomersList.as_view(), name='customers_list'),
    path('mycustomer/list/', views.CustomersList.as_view(), name='mycustomer_list'),
    path('customer/add/', views.CustomerOperate.as_view(), name='customer_add'),
    re_path('^customer/edit/(?P<edit_id>\d+)/$', views.CustomerOperate.as_view(), name='customer_edit'),
    re_path('^customer/delete/(?P<delete_id>\d+)/$', views.CustomerDelete.as_view(), name='customer_delete'),

    re_path('^consult_record/list/', views.ConsultRecordList.as_view(), name='consult_record_list'),
    path('consult_record/add/', views.ConsultRecordOperate.as_view(), name='consult_record_add'),
    re_path('^consult_record/edit/(?P<edit_id>\d+)/$', views.ConsultRecordOperate.as_view(), name='consult_record_edit'),
    re_path('^consult_record/delete/(?P<delete_id>\d+)/$', views.ConsultRecordDelete.as_view(), name='consult_record_delete'),

    path('class_study_record/list/', views.ClassStudyRecordList.as_view(), name='class_study_record_list'),
    path('class_study_record/add/', views.ClassStudyRecordOperate.as_view(), name='class_study_record_add'),
    re_path('^class_study_record/edit/(?P<edit_id>\d+)/$', views.ClassStudyRecordOperate.as_view(), name='class_study_record_edit'),
    re_path('^class_study_record/delete/(?P<delete_id>\d+)/$', views.ClassStudyRecordDelete.as_view(), name='class_study_record_delete'),

    re_path('^record/score/(\d+)/$', views.RecordScoreView.as_view(), name='record_score'),
    re_path('^customer/quantity/$', views.CustomerQuantity.as_view(), name='customer_quantity'),
]
