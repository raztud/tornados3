### Installation

pip install .

### Setup

You need to have the [AWS profile](http://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html) setup on the machine.
A basic usage would be:

```
root@dev:~# cat ~/.aws/config
[profile uploader]
region=eu-central-1
```
and

```
root@dev:~# cat ~/.aws/credentials
[uploader]
aws_access_key_id=<YOUR_KEY>
aws_secret_access_key=<YOUR_SECRET>
```

### Usage

See [example](example) folder.
