import json
import logging
from pathlib import Path
from predictor import bundle, predict

folder = Path(__file__).resolve().parent


def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    method = environ.get('REQUEST_METHOD', 'GET')
    status = '200 OK'
    content_type = 'application/json; charset=utf-8'
    if method == 'GET' and path in ['/', '/index.html']:
        body = (folder / 'index.html').read_bytes()
        content_type = 'text/html; charset=utf-8'
    else:
        if method == 'GET' and path == '/health':
            result = {'status': 'ok'}
        elif method == 'GET' and path == '/api/config':
            result = {'fuel_types': bundle['categories']['Fuel_Type'],
                      'transmissions': bundle['categories']['Transmission'],
                      'cutoff': bundle['cutoff']}
        elif method == 'POST' and path == '/api/predict':
            try:
                length = int(environ.get('CONTENT_LENGTH') or '0')
                if not 1 <= length <= 8192:
                    raise ValueError('Please send a valid set of car details.')
                details = json.loads(environ['wsgi.input'].read(length))
                if not isinstance(details, dict):
                    raise ValueError('Please send a valid set of car details.')
                result = predict(details)
            except (ValueError, TypeError) as error:
                status = '400 Bad Request'
                result = {'error': str(error)}
            except Exception:
                logging.exception('Prediction failed')
                status = '500 Internal Server Error'
                result = {'error': 'The estimate could not be calculated. Please try again.'}
        else:
            status = '404 Not Found'
            result = {'error': 'Page not found.'}
        body = json.dumps(result).encode('utf-8')
    start_response(status, [('Content-Type', content_type),
                            ('Content-Length', str(len(body))),
                            ('X-Content-Type-Options', 'nosniff')])
    return [body]


if __name__ == '__main__':
    import os
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', '8766'))
    print('Predictor: http://127.0.0.1:' + str(port), flush=True)
    make_server('127.0.0.1', port, application).serve_forever()
