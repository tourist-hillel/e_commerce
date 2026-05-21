from django.urls import include, path
from rest_framework.routers import DefaultRouter
from shop.api.views import CategoryViewSet, ProductViewSet, GetTokenPairView

router = DefaultRouter()

router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

app_name = 'shop_api'

urlpatterns = [
    path('', include(router.urls)),
    path('get-token/', GetTokenPairView.as_view(), name='jwt_token'),
]