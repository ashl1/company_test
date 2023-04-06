try:
    import httpx
except ImportError:
    try:
        import requests as httpx
    except ImportError:
        print('One of "httpx" or "requests" library must be installed')
        exit(1)

res = httpx.post('http://localhost:8000/stop_crawling')
print(res)

res = httpx.post(
    'http://localhost:8000/start_crawling',
    json={'url': 'https://en.wikipedia.org/wiki/Django_(web_framework)'},
)
print(res)

res = httpx.get('http://localhost:8000/status').text
print(res)

res = httpx.post('http://localhost:8000/stop_crawling')
print(res)