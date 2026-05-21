import functools
import logging
from django.core.cache import caches

logger = logging.getLogger(__name__)


L2 = caches['default']
L3 = caches['page_cache']

TTL_L2_PRODUCT = 5*60
TTL_L2_CATEGORY = 10*60
TTL_L2_USER = 3*60
TTL_L3_API = 2*60


def _product_key(product_id):
    return f'product:{product_id}'

def _product_slug_key(slug):
    return f'product:slug:{slug}'

def _category_key(category_id):
    return f'category:{category_id}'

def _category_list():
    return 'category:list'

def _category_child_list(parent_category_id):
    return f'category:{parent_category_id}:list'

def _user_orders_key(user_id):
    return f'user:{user_id}:orders'

def _api_response_key(path: str, query: str = ''):
    return f'api:{path}:{query[:200]}'

@functools.lru_cache(maxsize=256)
def get_active_category_ids():
    from shop.models import Category
    ids = frozenset(
        Category.objects.filter(is_active=True).values_list('id', flat=True)
    )
    logger.debug(f'[L1] active_category_ids loaded: count={len(ids)}')
    return ids

def get_cached_product(product_id):
    key = _product_key(product_id)
    data = L2.get(key)
    if data is not None:
        logger.debug(f'[L2 HIT] product_id={product_id}')
    else:
        logger.debug(f'[L2 MISS] product_id={product_id}')
    return data

def set_cached_product(product_id, data, timeout = TTL_L2_PRODUCT):
    key = _product_key(product_id)
    L2.set(key, data, timeout)
    logger.debug(f'[L2 SET] product_id={product_id}')

def get_cached_category_list():
    key = _category_list()
    data = L2.get(key)
    if data is not None:
        logger.debug(f'[L2 HIT] category:list')
    else:
        logger.debug(f'[L2 MISS] category:list')
    return data


def set_cached_category_list(data, timeout = TTL_L2_CATEGORY):
    key = _category_list()
    L2.set(key, data, timeout)
    logger.debug(f'[L2 SET] category:list') 


def get_cached_user_orders(user_id):
    key = _user_orders_key(user_id)
    data = L2.get(key)
    if data is not None:
        logger.debug(f'[L2 HIT] user orders user_id={user_id}')
    else:
        logger.debug(f'[L2 MISS] user orders user_id={user_id}')
    return data


def set_cached_user_orders(user_id, data, timeout=TTL_L2_USER):
    key = _user_orders_key(user_id)
    L2.set(key, data, timeout)
    logger.debug(f'[L2 SET] user orders user_id={user_id}')


def get_cached_api_response(path, query=''):
    key = _api_response_key(path, query)
    data = L3.get(key)
    if data is not None:
        logger.debug(f'[L3 HIT] api response path={path}, query={query}')
    else:
        logger.debug(f'[L3 MISS] api response path={path}, query={query}')
    return data


def set_cached_api_response(path, data, query='',  timeout = TTL_L3_API):
    key = _api_response_key(path, query)
    L3.set(key, data, timeout)
    logger.debug(f'[L3 SET] api response path={path}, query={query}')


def invalidate_product_cache(product_id, slug):
    L2.delete(_product_key(product_id))
    L2.delete(_product_slug_key(slug))
    L3.delete(_api_response_key('/api/products/', ''))
    L3.delete(_api_response_key(f'/api/products/{slug}', ''))
    logger.info(f'[CACHE INVALIDATE] product product_id={product_id}, slug={slug}')

def invalidate_category_cache(category_id):
    L2.delete(_category_key(category_id))
    L2.delete(_category_list())
    get_active_category_ids.cache_clear()
    logger.info(f'[CACHE INVALIDATE] category category_id={category_id}')

def invalidate_user_orders_cache(user_id):
    L2.delete(_user_orders_key(user_id))
    logger.info(f'[CACHE INVALIDATE] user orders user_id={user_id}')