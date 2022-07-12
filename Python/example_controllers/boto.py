import boto3

s3 = boto3.resource('s3')
bucket = s3.Bucket('tdw-public')

for obj in bucket.objects.filter(Prefix='vray_models/'):
    print(obj.key)