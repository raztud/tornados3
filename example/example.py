from tornado import gen
from tornado import ioloop

from tornados3 import S3AsyncManager

@gen.coroutine
def run():
    fh = open('./gnu.png')
    data = fh.read()
    fh.close()

    client = S3AsyncManager(profile_name='<YOUR_PROFILE_NAME>', bucket='<YOUR_BUCKET>')
    yield client.upload(body=data, path='path/to/gnu.png')

    # and to delete
    yield client.delete('path/to/gnu.png')


if __name__ == '__main__':
    ioloop.IOLoop.instance().run_sync(run)


