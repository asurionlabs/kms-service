###
# KMS Service is an AWS Lambda interface to interact with AWS KMS Key Encryption
# service.
# 
# Copyright (C) 2018-2019  Asurion, LLC
#
# KMS Service is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KMS Service is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with KMS Service.  If not, see <https://www.gnu.org/licenses/>.
###
  
import os
import sys
import json
import zlib
import base64
import logging
from datetime import datetime

import boto3
from Crypto.Cipher import AES

logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

AWS_KMS_KEY = os.environ["AWS_KMS_KEY"] if "AWS_KMS_KEY" in os.environ else ""


def getClient(technology, region="us-east-1"):
    try:
        session = boto3.Session(region_name=region)
        client = session.client(technology)
        return client
    except AttributeError as e:
        logger.info("Something went wrong, unable to create %s client" % (technology,))
        logger.exception(e)


def get_payload_body(payload):
    payload_body = {}

    if "kms_data" in payload.keys():
        payload_body = payload
    elif "body" in payload.keys():
        if isinstance(payload["body"], dict):
            logger.info("Received payload['body'] is a dictionary")
            payload_body = payload["body"]
        else:
            logger.info("Received payload['body'] was not a dictionary")
            payload_body = json.loads(payload["body"])
    
    return payload_body


def make_request(payload):
    # Get the Payload Body
    payload_body = {}
    
    # Check if the payload_body is a valid Dictionary
    if isinstance(payload, dict):
        logger.info("Recieved payload is a dictionary")
        payload_body = get_payload_body(payload)
    else:
        logger.info("payload is not a dictionary, running json.dumps()")
        payload_body = get_payload_body(json.loads(payload["body"]))

    if isinstance(payload_body, dict):
        # Get KMS Client
        kmsClient = getClient("kms")

        if "encrypt" in payload_body.keys() and payload_body["encrypt"]:
            logger.info("Encrypting Data...")

            # Compress Encryption Paylod and Get Encryption Payload Body
            encryption_blob = base64.b64encode(zlib.compress(payload_body["kms_data"].encode(), 9))
            
            # Generate a new Data Key for Encryption
            data_key = kmsClient.generate_data_key(KeyId=AWS_KMS_KEY, KeySpec="AES_256")

            # Payload to Encrypt
            encrypted_payload = {}
            encrypted_payload["ciphertext_blob"] = str(base64.b64encode(data_key["CiphertextBlob"]).decode())

            BLOCK_SIZE = 32
            PADDING = '{'
            pad = lambda data: data + (BLOCK_SIZE - len(data) % BLOCK_SIZE) * PADDING.encode()
            EncodeAES = lambda cipher, data: base64.b64encode(cipher.encrypt(pad(data)))
            aes_cipher = AES.new(data_key["Plaintext"])
            encrypted_data = EncodeAES(aes_cipher, encryption_blob)

            encrypted_payload["encrypted_payload"] = str(base64.b64encode(encrypted_data).decode())
            encrypted_payload["encryption_time"] = str(datetime.now())

            # Base64 Encode Data before returning
            encoded_encrypted_data = str(base64.b64encode(json.dumps(encrypted_payload, sort_keys=True, indent=2, separators=(',', ': ')).encode()).decode())

            # Create JSON Payload to return
            response = {"data": encoded_encrypted_data}

            return {
                "statusCode": 200,
                "body": json.dumps(response)
            }

        else:
            logger.info("Decrypting Data")

            # Get Decryption Blob from Payload Body
            decryption_blob = json.loads(base64.b64decode(payload_body["kms_data"] + "==="))

            # Get Decryption Key
            ciphertext_blob = base64.b64decode(decryption_blob["ciphertext_blob"])
            data_key = kmsClient.decrypt(CiphertextBlob=ciphertext_blob)

            # Decrypt the Message
            PADDING = '{'
            decodeAES = lambda cipher, data: cipher.decrypt(base64.b64decode(data)).rstrip(PADDING.encode())
            aes_cipher = AES.new(data_key["Plaintext"])
            decrypted_data = decodeAES(aes_cipher, base64.b64decode(decryption_blob["encrypted_payload"]))

            # Base64 Encode Data before returning
            encoded_decrypted_data = str(base64.b64encode(zlib.decompress(base64.b64decode(decrypted_data))).decode())
            
            # Create JSON Payload to return
            response = {"data": encoded_decrypted_data}

            return {
                "statusCode": 200,
                "body": json.dumps(response)
            }

    else:
        logger.error("Input is not a Dictionary!")


def lambda_handler(event, context):
    return make_request(event)
