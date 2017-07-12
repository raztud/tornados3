import boto3
import logging

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest, HTTPError

from botocore.handlers import calculate_md5
from botocore.awsrequest import AWSRequest
from botocore.auth import S3SigV4Auth

log = logging.getLogger(__name__)

AsyncHTTPClient.configure('tornado.curl_httpclient.CurlAsyncHTTPClient')


class S3AsyncManager(object):

    proxyHost = None
    proxyPort = None

    def __init__(self, profile_name, bucket):
        """
        Creates a new S3AsyncManager object.
        It will use AsyncHTTPClient as http client to interact with AWS S3.

        :param profile_name: The AWS Profile name
        :param bucket: The S3 bucket to work on
        """
        session = boto3.Session(profile_name=profile_name)
        self.credentials = session.get_credentials()
        self.region = session.region_name
        self.bucket = bucket
        self.client = AsyncHTTPClient()

    @gen.coroutine
    def upload(self, body, path, acl=None):
        """
        Uploads the body bytes in S3 in the specified path.

        :param body: The body as bytes
        :param path: The path where to be saved in S3 (eg: images/medium/file.jpg)
        :param acl: The S3 ACL
        :return: The URL from S3
        :rtype: string
        :raise: HTTPError | Exception
        """

        url = self.__getUrl(path)

        headers = self.get_headers(url=url, body=body, method='PUT', acl=acl)

        request = {
            'method': 'PUT',
            'url': url,
            'headers': headers,
            'body': body,
            'validate_cert': True,
            'proxy_host': self.proxyHost, #'proxy.buh1.avira.org',
            'proxy_port': self.proxyPort, # 3128,
        }

        try:
            response = yield self.client.fetch(HTTPRequest(**request))
        except HTTPError as err:
            log.error("HTTPError calling AWS S3: {}, {} {}".format(err, err.message, err.code))
            request['body'] = 'DUMMY'
            log.error("Request: {}".format(request))
            raise err
        except Exception as e:
            log.error("Exception calling AWS S3: {}".format(e))
            raise e

        raise gen.Return(response.effective_url)

    @gen.coroutine
    def delete(self, path):
        """
        Delete the specified file from S3.

        :param path: The path to file in s3. Eg: medium/file.jpg
        :return: True on success
        :rtype: bool
        :raise: HTTPError | Exception
        """
        url = self.__getUrl(path)

        headers = self.get_headers(url=url, method='DELETE')
        request = {
            'method': 'DELETE',
            'url': url,
            'headers': headers,
            'validate_cert': True,
            'proxy_host': self.proxyHost,
            'proxy_port': self.proxyPort,
        }

        try:
            yield self.client.fetch(HTTPRequest(**request))
        except HTTPError as err:
            log.error("HTTPError calling AWS S3: {}".format(err))
            raise err
        except Exception as e:
            log.error("Exception calling AWS S3: {}".format(e))
            raise e

        raise gen.Return(True)

    def get_headers(self, url, method, body=None, acl=None):
        """
        Returns the necessary headers to do a http request to AWS S3.

        :param url: The full url of the file from S3
        :param method: The HTTP method to to be used (PUT, DELETE)
        :param body: The body to upload, as bytes (only for PUT)
        :param acl: The S3 ACL
        :return: The necessary headers to do an HTTP request to S3
        :rtype: dict
        """

        keys = ['X-Amz-Date',
                'X-Amz-Content-SHA256',
                'Authorization', ]

        headers = {}
        if method == 'PUT':
            headers = {
                'Content-MD5': self.getBodyMd5(body),
                'Expect': '100-continue',
            }

            keys = keys + ['Expect', 'Content-MD5']

            if acl:
                headers['x-amz-acl'] = acl
                keys.append('x-amz-acl')

        request = AWSRequest(method.upper(), url, data=body, headers=headers)

        signer = S3SigV4Auth(credentials=self.credentials, service_name='s3', region_name=self.region)
        signer.add_auth(request)

        allHeaders = {}
        for key in keys:
            allHeaders[key] = request.headers[key]

        return allHeaders

    def getBodyMd5(self, body):
        """
        Returns the md5 for the bytes from body.
        :param body:
        :return: md5(body)
        :rtype: str
        """
        req = {
            'body': body,
            'headers': {}
        }
        calculate_md5(req)
        return req['headers']['Content-MD5']

    def setProxy(self, host, port):
        self.proxyHost = host if host else None
        self.proxyPort = port if port else None

    def __getUrl(self, path):
        """
        Returns the S3 full url

        :param path: The path where the file should be.
        :type path: str
        :return: The full S3 url.
        :rtype: str
        """
        host = 's3-{region}.amazonaws.com'.format(region=self.region)
        url = 'https://{host}/{bucket}/{filename}'.format(host=host,
                                                          bucket=self.bucket,
                                                          filename=path)
        return url
