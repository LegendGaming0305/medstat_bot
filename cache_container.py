from aiocache import caches, SimpleMemoryCache

# Создаем кэш хранилище
cache = SimpleMemoryCache()

# Настройки хранилища
caches.set_config({
    'default':  {
        'cache': 'aiocache.SimpleMemoryCache',
        'serializer': {
            'class': 'aiocache.serializers.PickleSerializer'
        }
    }
})

class Data_storage:
    question_id = 0