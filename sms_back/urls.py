from django.urls import include, path
from rest_framework import routers
from apis import views as apis_views
from rest_framework.authtoken import views
from apis.views import CustomAuthTokenView, CustomUserUpdateView
from apis.views import academic_years, metrics, graph

router = routers.DefaultRouter()
# router.register(r'users', apis_views.UserViewSet)
router.register(r'groups', apis_views.GroupViewSet)
router.register(r'classes', apis_views.ClassViewSet)
router.register(r'students', apis_views.StudentViewSet)
router.register(r'subjects', apis_views.SubjectViewSet)
router.register(r'teachers', apis_views.TeacherViewSet)
router.register(r'cashin', apis_views.CashInViewSet)
router.register(r'cashout', apis_views.CashOutViewSet)
router.register(r'marks', apis_views.MarkViewSet)
router.register(r'results', apis_views.ResultViewSet)
router.register(r'users', apis_views.CustomUserViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', CustomAuthTokenView.as_view(), name='api-token-auth'),
    path('custom_user/', CustomUserUpdateView.as_view(), name='custom-user-update'),
    path('years/', academic_years, name='hello_world'),
    path('metrics/', metrics, name='metrics'),
    path('graph/', graph, name='graph')
]