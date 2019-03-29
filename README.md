# KMS Service
---

This lambda function encrypts/decrypts data using AWS KMS and returns a base64 encoded string of the encrpyted/decrypted payload.

Licensed under the GNU General Public License ver3 or later. GNU General Public License: http://www.gnu.org/licenses/

#### Platform: Python 3.6

## Instructions

Building Lambda functions on your host machine running Windows or Mac OS may not build lambda functions properly and may cause issues when executing on AWS. Compiling lambda functions for certain runtimes where the dependencies are compiled differently for each host OS is the culprit here. Hence the best way to ensure that the lambda function will execute seamlessly on AWS is to make sure that you compile it in an environment similar to where its going to run in. 

TLDR; Please remember building lambda functions can be tricky. Its best to build it in an environment similar to the one its going to be run in, as sometime not doing so can create modules or dependency issues.

## How to Build

Building the function is really simple. You will need docker installed and setup on your machine to be able to build. To install docker, visit [https://www.docker.com/get-started](https://www.docker.com/get-started). 

Once you have docker installed and running, use the attached docker-compose file and it will take care of the whole building process. This can be done using

```
docker-compose up
```

This will build the docker image first if you don't already have one built, and then run the build command and output a deployable zip file in `target` folder. At this point if you already know your way around lambda function you can take the zip and deploy to the lambda.


## Setting up

You can trigger this lambda from any aws service with the payload listed below. If triggering from API Gateway you can select proxy pass for method integration if you wish capture extra information within lambda or just add a trigger to the lambda.

>**Note:** It requires you to define `AWS_KMS_KEY` as an environment variable where the value of will be KMS key that you wish to use in for encryption/decryption.

### IAM Role for Lambda

Below is a copy for the role permissions that the lambda function will require.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "kms:ListKeys",
                "kms:Decrypt",
                "kms:GenerateRandom",
                "kms:Encrypt",
                "kms:GenerateDataKey",
                "kms:GenerateDataKeyWithoutPlaintext",
                "kms:DescribeKey",
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

## Using the function

### Encrpyting Data

#### Encrypt

Setting `encrypt` to true will encrypt the value of `kms_data` and return a base64 encoded string in response body.

```json
{
    "kms_data": "sample_text",
    "encrypt": true
}
```

#### Encrypt Response Body

Here is a sample response body where encrypt is set to true.

```json
{
    "data":"ewogICJjaXBoZXJ0ZXh0X2Jsb2IiOiAiY2lwaGVydGV4dF9ibG9iIiwKICAiZ2VuZXJhdGVkX3RpbWVfdXRjIjogIjIwMTktMDMtMTggMDU6MDA6NTguNTA5NzA0IiwKICAiZW5jcnlwdGVkX3BheWxvYWQiOiAiZW5jcnlwdGVkX3BheWxvYWQiCn0="
}
```

#### Base64 Decoded Response Body

Since the body value of `data` is base64 enconded its a single string, however below is what you should expect in the response once base64 decoded.

```json
{
    "ciphertext_blob": "ciphertext_blob",
    "encrpytion_time": "2019-03-18 05:00:58.509704",
    "encrypted_payload": "encrypted_payload"
}
```

### Decrypting Data

#### Decrypt

Setting `encrypt` to false will decrypt the value of `kms_data` and return a base64 encoded string in response body. 

```json
{
    "kms_data": "ewogICJjaXBoZXJ0ZXh0X2Jsb2IiOiAiY2lwaGVydGV4dF9ibG9iIiwKICAiZ2VuZXJhdGVkX3RpbWVfdXRjIjogIjIwMTktMDMtMTggMDU6MDA6NTguNTA5NzA0IiwKICAiZW5jcnlwdGVkX3BheWxvYWQiOiAiZW5jcnlwdGVkX3BheWxvYWQiCn0=",
    "encrypt": false
}
```

#### Decrypt Response Body

Sample Base64 encoded string in response body.

```json
{
    "data": "dGVzdA=="
}
```

#### Base64 Decoded Response Body

Since the body value of `data` is base64 enconded its a single string, however below is what you should expect in the response once base64 decoded.

```
test
```