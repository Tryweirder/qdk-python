#!/bin/env python
# -*- coding: utf-8 -*-
##
# recording_updater.py: Updates test recordings with dummy values
##
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
##

## IMPORTS ##

import os
import re
import unittest.mock
from azure.quantum import Workspace
from azure.common.credentials import ServicePrincipalCredentials
from msrest.authentication import BasicTokenAuthentication
from azure_devtools.scenario_tests.base import ReplayableTest
from azure_devtools.scenario_tests.recording_processors import RecordingProcessor, is_text_payload, AccessTokenReplacer

class QuantumTestBase(ReplayableTest):
    """QuantumTestBase
    
    During init, gets Azure Credentials and Azure Quantum Workspace parameters from OS environment variables.
    """

    dummy_uid = "00000000-0000-0000-0000-000000000000"
    dummy_rg = "dummy-rg"
    dummy_ws = "dummy-ws"
    dummy_clientsecret = "sanitized"
    dummy_auth_token = {'access_token': 'eyJ1eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyIsImtpZCI6Im5PbzNaRHJPRFhFSzFqS1doWHNsSFJfS1hFZyJ9.eyJidWQiOiJodHRwczovL3F1YW50dW0ubWljcm9zb2Z0LmNvbSIsImlzcyI6Imh0dHBzOi8vc3RzLndpbmRvd3MubmV0LzcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0Ny8iLCJpYXQiOjE2MTE2ODMwNjAsIm5iZiI6MTYxMTY4MzA2MCwiZXhwIjoxNjExNjg2OTYwLCJfY2xhaW1fbmFtZXMiOnsiZ3JvdXBzIjoic3JjMSJ9LCJfY2xhaW1fc291cmNlcyI6eyJzcmMxIjp7ImVuZHBvaW50IjoiaHR0cHM6Ly9ncmFwaC53aW5kb3dzLm5ldC83MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDcvdXNlcnMvZTlhNGE5ZTEtODcxNS00Yjc1LTk2NWQtYzBkZDQxMTIzODY4L2dldE1lbWJlck9iamVjdHMifX0sImFjciI6IjEiLCJhaW8iOiJBVlFBcS84U0FBQUFXMnNsMlRORXd5eXA2OGdvejM2RnRoSXFZSlJDdmRibDF0WVJPanUrUzNCZDV5MGsyeWMyOFdKUk9IQ283a0VuNGRpaDh1dkpLQm00TFNoTHRUQ3FsMHMwNkp6N3NYclNpNTFJOEljZThZcz0iLCJhbXIiOlsid2lhIiwibWZhIl0sImFwcGlkIjoiODRiYTA5NDctNmM1My00ZGQyLTljYTktYjM2OTQ3NjE1MjFiIiwiYXBwaWRhY3IiOiIwIiwiZmFtaWx5X25hbWUiOiJCcm93biIsImdpdmVuX25hbWUiOiJUb20iLCJpbl9jb3JwIjoidHJ1ZSIsImlwYWRkciI6IjczLjgzLjM5LjEwIiwibmFtZSI6IlRvbSBCcm93biIsIm9pZCI6ImU5YTRhOWUxLTg3MTUtNGI3NS05NjVkLWMwZGQ0MTEyMzg2OCIsIm9ucHJlbV9zaWQiOiJTLTEtNS0yMS0yMTI3NTIxMTg0LTE2MDQwMTI5MjAtMTg4NzkyNzUyNy0xNzc1MDU1MSIsInB1aWQiOiIxMDAzN0ZGRTkyREI4MzEyIiwicmgiOiIwLkFSb0F2NGo1Y3ZHR3IwR1JxeTE4MEJIYlIwY0p1b1JUYk5KTm5LbXphVWRoVWhzYUFPOC4iLCJzY3AiOiJKb2JzLlJlYWRXcml0ZSIsInN1YiI6IjNxVk1XZ3cxRWozYVRlTEdTenE0bmVsMms1UHFVS1BBY2ZVNDBSUl9JZ3MiLCJ0aWQiOiI3MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDciLCJ1bmlxdWVfbmFtZSI6InRoYnJvQG1pY3Jvc29mdC5jb20iLCJ1cG4iOiJ0aGJyb0BtaWNyb3NvZnQuY29tIiwidXRpIjoiUzMxNVVqbk9JVWUzeDdRR3ZaVWFBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il19.PCWEtCdso3_jehm3Ppg9lCSy_VgwY96IG0_Lqji5tN3yEmBmsP4Du-6MA2IHlz7pbKfQ8Qdw4aeobWZkuDW71Zo9PCkBSLQewng5EMbDvZO3jPJfCOd0IepaPVdtvtaCL2KnPEZicEM4kIO_9f8hCC4Ik8MAem788HuutNhN_YExJDWtM-aNoXIBLtDm39u3bCr2WFk4he3xpISLD3ZqAk2UPKagMwuwO-tArtcoQvA1_n_owv-I5P8vEk1wOmUh6LTB6pUAIS4wFIMgINUE1dBSuQmyimEfc7rRuWl-YJrMH0WRdbgFutwbBv_5dKs6VcYGgrvA3nIGU_Xz5vuJMA', 'token_type': 'Bearer', 'expires_in': 485}

    def __init__(self, method_name):
        self._client_id = os.environ.get("AZURE_CLIENT_ID", self.dummy_uid)
        self._client_secret = os.environ.get("AZURE_CLIENT_SECRET", self.dummy_clientsecret)
        self._tenant_id = os.environ.get("AZURE_TENANT_ID", self.dummy_uid)
        self._resource_group = os.environ.get("RESOURCE_GROUP", self.dummy_rg)
        self._subscription_id = os.environ.get("SUBSCRIPTION_ID", self.dummy_uid)
        self._workspace_name = os.environ.get("WORKSPACE_NAME", self.dummy_ws)

        regex_replacer = CustomRecordingProcessor()
        recording_processors = []
        recording_processors.append(regex_replacer)
        recording_processors.append(AccessTokenReplacer())
        replay_processors = []
        
        super(QuantumTestBase, self).__init__(method_name, recording_processors=recording_processors, replay_processors=replay_processors)

        if not (self.in_recording or self.is_live):
            self._client_id = self.dummy_uid
            self._client_secret = self.dummy_clientsecret
            self._tenant_id = self.dummy_uid
            self._resource_group = self.dummy_rg
            self._subscription_id = self.dummy_uid
            self._workspace_name = self.dummy_ws

        regex_replacer.register_regex(self.client_id, self.dummy_uid)
        regex_replacer.register_regex(self.client_secret, self.dummy_clientsecret)
        regex_replacer.register_regex(self.tenant_id, self.dummy_uid)
        regex_replacer.register_regex(self.subscription_id, self.dummy_uid)
        regex_replacer.register_regex(self.workspace_name, self.dummy_ws)
        regex_replacer.register_regex(self.resource_group, self.dummy_rg)
        regex_replacer.register_regex(r'/subscriptions/([a-f0-9]+[-]){4}[a-f0-9]+', "/subscriptions/" + self.dummy_uid)
        regex_replacer.register_regex(r'job-([a-f0-9]+[-]){4}[a-f0-9]+', "job-" + self.dummy_uid)
        regex_replacer.register_regex(r'jobs/([a-f0-9]+[-]){4}[a-f0-9]+', "jobs/" + self.dummy_uid)
        regex_replacer.register_regex(r'"id":\s*"([a-f0-9]+[-]){4}[a-f0-9]+"', '"id": "{}"'. format(self.dummy_uid))
        regex_replacer.register_regex(r'/resourceGroups/[a-z0-9-]+/', "/resourceGroups/dummy-rg/")
        regex_replacer.register_regex(r'/workspaces/[a-z0-9-]+/', "/workspaces/dummy-ws/")
        regex_replacer.register_regex(r'sig=[0-9a-zA-Z%]+\&', "sig=sanitized&")
        regex_replacer.register_regex(r'sv=[^&]+\&', "sv=sanitized&")
        regex_replacer.register_regex(r'se=[^&]+\&', "se=sanitized&")

    def setUp(self):
        super(QuantumTestBase, self).setUp()
        # mitigation for issue https://github.com/kevin1024/vcrpy/issues/533
        self.cassette.allow_playback_repeats = True

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def resource_group(self):
        return self._resource_group

    @property
    def subscription_id(self):
        return self._subscription_id

    @property
    def workspace_name(self):
        return self._workspace_name

    def create_workspace(self) -> Workspace:
        """Create workspace using credentials stored in config file

        :return: Workspace
        :rtype: Workspace
        """

        workspace = Workspace(
        
            subscription_id=self.subscription_id,
            resource_group=self.resource_group,
            name=self.workspace_name,
        )

        if self.is_live or self.in_recording:
            workspace.credentials = ServicePrincipalCredentials(
                tenant=self.tenant_id,
                client_id=self.client_id,
                secret=self.client_secret,
                resource  = "https://quantum.microsoft.com"
            )
            workspace.login(False)
        else:
            workspace.credentials = BasicTokenAuthentication(token=self.dummy_auth_token)

        return workspace

class CustomRecordingProcessor(RecordingProcessor):

    ALLOW_HEADERS = [
        'content-length',
        'content-type',
        'accept',
        'accept-encoding',
        'accept-charset',
        'accept-ranges',
        'x-ms-range',
        'transfer-encoding',
        'x-ms-blob-content-md5',
        'x-ms-blob-type',
        'x-ms-creation-time',
        'x-ms-lease-state',
        'x-ms-lease-status',
        'x-ms-server-encrypted',
        'x-ms-version'
        ]
    
    def __init__(self):
        self._regexes = []

    def register_regex(self, oldRegex, new):
        self._regexes.append((re.compile(oldRegex), new))

    def process_request(self, request):
        headers = {}
        for key in request.headers:
            if key.lower() in self.ALLOW_HEADERS:
                headers[key] = request.headers[key]
        #request.headers = headers

        for oldRegex, new in self._regexes:
            request.uri = oldRegex.sub(new, request.uri)            

        if _get_content_type(request) == "application/x-www-form-urlencoded":
            body = request.body.decode("utf-8")
            for oldRegex, new in self._regexes:
                body = oldRegex.sub(new, body)
            request.body = body.encode("utf-8")
        else:
            body = str(request.body)
            for oldRegex, new in self._regexes:
                body = oldRegex.sub(new, body)
            request.body = body

        return request

    def process_response(self, response):
        import six

        headers = {}
        for key in response['headers']:
            if key.lower() in self.ALLOW_HEADERS:
                headers[key.lower()] = response['headers'][key]
        #response['headers'] = headers

        if is_text_payload(response):
            body = response['body']['string']
            if not isinstance(body, six.string_types):
                body = body.decode("utf-8")
            if is_text_payload(response) and body:
                for oldRegex, new in self._regexes:
                    body = oldRegex.sub(new, body)            
                response['body']['string'] = body

        return response

