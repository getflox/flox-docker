from schema import Optional, And, Use


def config():
    return {
        Optional('docker'): {
            Optional('repository'): str,
        }
    }
