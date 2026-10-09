"""Start Netra's local web UI and API with one worker."""
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Netra: read-only Microsoft Entra assistant')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8001)
    parser.add_argument('--reload', action='store_true', help='Reload backend changes during local development')
    args = parser.parse_args()
    os.chdir(Path(__file__).resolve().parent)
    import uvicorn
    uvicorn.run('src.api.main:app', host=args.host, port=args.port, reload=args.reload, workers=1)


if __name__ == '__main__':
    main()
