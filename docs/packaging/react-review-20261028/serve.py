"""Serve the extracted review package on localhost and open its React welcome."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import webbrowser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0, help='Local port; 0 chooses a free port.')
    parser.add_argument('--no-browser', action='store_true', help='Print URLs without opening a browser.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if not (root / 'react-preview/dist/index.html').is_file():
        parser.error('Extract the complete ZIP before running serve.py.')
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as error:
        parser.exit(1, 'Cannot start local server: ' + str(error) + '\nTry --port 0.\n')
    with server:
        base = 'http://127.0.0.1:' + str(server.server_port) + '/'
        url = base + 'react-preview/dist/#/'
        print('REACT: ' + url, flush=True)
        print('MAIN WELCOME: ' + base + 'design/welcome-proposal.html', flush=True)
        print('Keep this window open. Stop with Ctrl+C.', flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
