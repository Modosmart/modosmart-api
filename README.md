# [ModoSmart Symbiote](http://www.modosmart.com/)

This repository contains the Modosmart API service that should be consumed on behalf of the client by [Symbiote Smart Space](https://github.com/symbiote-h2020/SymbioteSmartSpace) to connect to Modosmart devices over BLE and WiFi.

On startup this application will scan for nearby Room Sensors and Ac Switch and will register those devices on Symbiote Core, so that later client application (mobile phone) could learn about the available devices.

### What is Symbiote
symbIoTe is an interoperable ecosystem where any IoT platform and/or resource can interact in a trusted and unified way.

symbIoTe is an Open Source middleware which allows IoT solutions providers to expose, share and exchange their resources.

For more info about Symbiote visit [Symbiote](https://www.symbiote-h2020.eu/).

### Architecture
![Architecture](https://raw.githubusercontent.com/Modosmart/modosmart-api/master/resources/diagram.png)


### Symbiote Core and Symbiote Cloud
Modosmart is L3 Compliant ecosystem with public Symbiote Core and Symbiote Cloud.

In order for Modosmart to be L3 compliant, it should consume services from public Symbiote Core and Cloud, and for that to happen an account should be created through [Admin UI](https://symbiote-open.man.poznan.pl/administration).

After user configuration on symbiote core and adding our SSP (Symbitoe Smart Space), the information should be later used to configure AuthenticationAuthorizationManager and SymbioteSmartSpace running on gateway.

### [Authentication Authorization Manager](https://github.com/symbiote-h2020/AuthenticationAuthorizationManager)
1. AAM certificate keystore and bootstrap.properties files should be created and placed in the resources folder precompiling the project.
2. Steps from [wiki](https://github.com/symbiote-h2020/SymbioteSmartSpace/wiki/2.3-Setting-up-the-SSP-Authentication-and-Authorization-Manager-(SspAAM-aka-LocalAAM) should be followed to create those files.
3. The files created can be found [here](https://github.com/Modosmart/modosmart-api/tree/master/config/AuthenticationAutorization)

Authentication Authorization Manager is running on port 8443.

### Symbiote Smart Space
To start Symbiote Smart Space those [steps should be followed](https://github.com/symbiote-h2020/SymbioteSmartSpace/wiki/2.4-Starting-Symbiote-Smart-Space).

configuration of SSP is done through [application.properties](https://github.com/Modosmart/modosmart-api/tree/master/config/SymbioteSmartSpace) file.

SSP will be running on port 8081, and a DNS should point to SSP so it's reachable from external networks.

DNS used is https://symbioteweb.eu.ngrok.io
* ## Public resources
GET https://symbioteweb.eu.ngrok.io/innkeeper/public_resources

this endpoint is used to get all available resource registered to the Symbiote Core.
* ## Inkeeper endpoint
The inkeeper endpoint is used to register, unregister, join.

 The following interfaces are shown as plain text Json request, but please take in mind that you should cypth this data using the LWSP message mti=0x50 (for the request from agent to innkeeper). For the response coming from the innkeeper the same story, here are shown the response as plain text, but remember that you should expect a message with mti=0x60 and decrypting the "data" field you get back the Json response.

| Interface  | path | From  | To | Description |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| register SDEV  | https://symbioteweb.eu.ngrok.io/innkeeper/sdev/register/  | agent  | Innkeeper  | Registers SDEV.  |
| join  | https://symbioteweb.eu.ngrok.io/innkeeper/sdev/join/  | agent  | Innkeeper  | Register every single resource of the agent.  |
| keep-alive  | https://symbioteweb.eu.ngrok.io/innkeeper/keep_alive/  | agent  | Innkeeper  | Notify that SDEV is alive  |
| unregister SDEV | https://symbioteweb.eu.ngrok.io/innkeeper/sdev/unregister | agent | Innkeeper | De-register the SDEV in the SSP |


 ##### Register
 Request:
 ```
  {
    "symId": "",
    "pluginId": "55:66:77:3a:61:76",
    "sspId": "",
    "roaming": false,
    "pluginURL": "http://10.20.30.5/rap/v1/request",
    "dk1": "5f6377981f97fb5be6d6dfbb3a32e372",
    "hashField": "00000000000000000000"
  }
 ```
 Where:
 * "symId" is the symbiote Id, if it is the first time ever the SDEV connects to a SSP or not a roaming SDEV it could be empty, otherwise is the assigned symbiote Id (SDEV thus need to save the symId returned from the Innkeeper in the last registration)
 * "pluginId" is the name with which the Agent recognize itself in the SSP. it is the identifier used from the RAP to address request to the agent.
 * "sspId" is the local identifier of the agent inside the SSP, used in case of no internet connectivity
 * "pluginURL" is the URL at which the agent respond at the RAP data request
 * "dk1" it is the derived key of the LWSP
 * "hashfield" is a field used in roaming. if it is the first time ever the SDEV connects to a SSP or not a roaming SDEV it is "00000000000000000000", otherwise it is calculated as follows:

 hashfield = SHA1(symIdSDEV || previous dk1)

 Response:
 ```
  {
    "symId": "",
    "sspId": "4",
    "result": "OFFLINE",
    "registrationExpiration": 3600
  }
 ```
Where:
* "symId" is the assigned symbiote Id, it could be empty if the SSP has no internet connection
* "sspId" is the local identifier of the agent inside the SSP, used in case of no internet connectivity
* "result" it is the result of the Register, it could be "OK", "REJECT", "ALREADY_REGISTERED"
* "registrationExpiration" is the alive time of this registratin, SDEV should send periodically keep-alive message to refresh this expiration time. Value time is in milliseconds.

 ##### Join

 Request as plain Text:

 ```
    {
        "internalIdResource": "5c:cf:7f:3a:6b:76",
        "sspIdResource": "",
        "sspIdParent": "4",
        "symIdParent": "",
        "accessPolicy": {
          "policyType": "PUBLIC",
          "requiredClaims": {}
        },
        "filteringPolicy": {
          "policyType": "PUBLIC",
          "requiredClaims": {}
        },
        "resource": {
          "@c": ".Actuator",
          "id": "",
          "name": "ACT-SDEV_6B:76",
          "description": null,
          "interworkingServiceURL": "http://10.20.30.5/rap/v1/request",
          "locatedAt": null,
          "services": null,
          "capabilities": [
            {
              "name": "RGBCapability",
              "parameters": [
                {
                  "name": "r",
                  "datatype": {
                    "@c": ".PrimitiveDatatype",
                    "baseDatatype": "xsd:unsignedByte",
                    "isArray": false
                  },
                  "mandatory": true,
                  "restrictions": [
                    {
                      "@c": ".RangeRestriction",
                      "min": 0,
                      "max": 255
                    }
                  ]
                },
                {
                  "name": "g",
                  "datatype": {
                    "@c": ".PrimitiveDatatype",
                    "baseDatatype": "xsd:unsignedByte",
                    "isArray": false
                  },
                  "mandatory": true,
                  "restrictions": [
                    {
                      "@c": ".RangeRestriction",
                      "min": 0,
                      "max": 255
                    }
                  ]
                },
                {
                  "name": "b",
                  "datatype": {
                    "@c": ".PrimitiveDatatype",
                    "baseDatatype": "xsd:unsignedByte",
                    "isArray": false
                  },
                  "mandatory": true,
                  "restrictions": [
                    {
                      "@c": ".RangeRestriction",
                      "min": 0,
                      "max": 255
                    }
                  ]
                }
              ],
              "effects": null
            }
          ]
        }
       }
   ```

 Where:

 * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests.
 * "sspIdResource" is the sspId of that resource, it is returned from the innkeeper
 * "sspIdParent" is the sspId os the container SDEV
 * "symIdParent" is the symbioteId of the SspSDEVInfo class, the "conteiner" SDEV of that resource
 * "accessPolicy" is the accessPolicy class, for a public resource you can use the description shown in the example
 * "filteringPolicy" is the filtering class, for a public resource you can use the description shown in the example
 * "resource" is the resource class that describes the semantic of the resource

 Response:

 ```
 {
      "registrationExpiration": 3600,
      "symIdResource": "",
      "sspIdResource": "0",
      "symId": "",
      "sspId": "4",
      "result": "OFFLINE"
 }

 ```

 Where:

 * "registrationExpiration" is the alive time of this registration, SDEV should send periodically keep-alive message to refresh this expiration time. Value time is in milliseconds.
 * "symIdResource" is the retuned symbioteId of the resource
 * "sspIdResource" is the sspId of that resource
 * "symId" is the symbioteId of the SspSDEVInfo class, the "conteiner" SDEV of that resource
 * "result" it is the result of the Join, it could be "OK", "REJECT", "ALREADY_REGISTERED"

 ##### Keep Alive
 Request:

 ```
 {
   "sspId": "4"
 }

 ```

 Where:

 * "sspId" is the sspId of the SDEV container, the SspSDEVInfo class

 Response:

 ```
 {
    "symId": "",
    "sspId": "4",
    "result": "OFFLINE",
    "updatedSymId": [
      {
        "sspIdResource": "0",
        "symIdResource": ""
      },
      {
        "sspIdResource": "1",
        "symIdResource": ""
      }
    ]
 }

 ```

 Where:

 * "symId" is the symbioteId of the SspSDEVInfo class, the "conteiner" SDEV of that resource
 * "sspId" is the sspId os the container SDEV
 * "result" it is the status of SSP, it could be "ONLINE" or "OFFLINE"
 * "updatedSymId" is a list of updated identifier for the resources. It could be useful if the SSP change its status form OFFLINE to ONLINE

 ##### unregister SDEV

 Request:

 ```
 {
   "sspId": "4"
 }

 ```

 Where:

 * "sspId" is the sspId of the SDEV container, the SspSDEVInfo class

 Response:
 It is just a HTTP 200.

  Payload sent on the http requests should be encrypted using [LWSP Protocol](https://github.com/symbiote-h2020/LWSPLibrary)

 * ## Rap endpoint
 The rap endpoint is used to get the readings from the devices, or control actuators.
 The rap will create a http request on behalf of the client to the url configured while registering the device.

 An agent should be created on the Modosmart-Api service which handle those endpoints.

 These interfaces, are sent as plain-text Json in the body of the HTTP POST:

| Interface     | path        | From | To   | Description |
| ------------- |-------------| -----| -----| ------------|
| RAP GET       | https://symbioteweb.eu.ngrok.io/rap/v1/request | RAP | Agent | Get data from the agent |
| RAP HISTORY   | https://symbioteweb.eu.ngrok.io/rap/v1/request | RAP | Agent | Get historic data from the agent |
| RAP SUBSCRIBE | https://symbioteweb.eu.ngrok.io/rap/v1/request | RAP | Agent | Request a push subscription of data from agent |
| RAP UNSUBSCRIBE | https://symbioteweb.eu.ngrok.io/rap/v1/request | RAP | Agent | Delete the subscribe request |
| RAP SET       | https://symbioteweb.eu.ngrok.io/rap/v1/request | RAP | Agent | Actuate the resource from the agent |

##### RAP GET
Request from RAP:

 ```

  {
    "resourceInfo": [
      {
        "symbioteId": "",
        "internalIdResource": "5c:cf:7f:3a:6b:76",
        "type": "Light"
      },
      {
        "type": "Observation"
      }
    ],
    "type": "GET"
  }

 ```

 Where:

 * "resourceInfo":

     * "symbioteId" is the symbiote-Id of the SDEV
     * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests
     * "type" is the semantic type of the resource that RAP wants to get information, it is related to the semantic description of the resource.
     * "type": "Observation", always as this.
 * "type": "GET", always as this.

 Response from Agent:

```
          {
            "resourceId": "5c:cf:7f:3a:6b:76",
            "location": {
              "longitude": -2.944728,
              "latitude": 43.26701,
              "altitude": 20
            },
            "resultTime": "1970-1-1T02:00:12",
            "samplingTime": "1970-1-1T02:00:12",
            "obsValues": [
              {
                "value": "25.19",
                "obsProperty": {
                  "@c": ".Property",
                  "name": "temperature",
                  "description": ""
                },
                "uom": {
                  "@c": "UnitOfMeasurment",
                  "symbol": "°C",
                  "name": "°C",
                  "description": ""
                }
              },
              {
                "value": "1009.34",
                "obsProperty": {
                  "@c": ".Property",
                  "name": "pressure",
                  "description": ""
                },
                "uom": {
                  "@c": "UnitOfMeasurment",
                  "symbol": "mBar",
                  "name": "mBar",
                  "description": ""
                }
              }
            ]
          }


 ```

 Where:

 * "resourceId" is the resource identifier, the internalIdResource.
 * "location" is a Json with the geographic collocation, you can leave also as null if no information available
 * "longitude" is the longitude
 * "latitude" is the latitude
 * "altitude" is the altitude
 * "resultTime" is time of the end of measurement
 * "samplingTime" is the time of the start of the measurement
 * "obsValues" is the ObservationValue Class, as defined in the CIM (Core Information Model) https://github.com/symbiote-h2020/SymbIoTeLibraries/tree/master/src/main/java/eu/h2020/symbiote/model/cim
 * "uom" is the UnitOfMeasurment Class, as defined in the CIM (Core Information Model) https://github.com/symbiote-h2020/SymbIoTeLibraries/tree/master/src/main/java/eu/h2020/symbiote/model/cim


 ##### RAP HISTORY

 Request from RAP:

 ```

 {
    "resourceInfo": [
      {
        "symbioteId": "",
        "internalIdResource": "5c:cf:7f:3a:6b:76",
        "type": "Light"
      },
      {
        "type": "Observation"
      }
    ],
    "type": "HISTORY"
 }

 ```

Where:

* "resourceInfo":

    * "symbioteId" is the symbiote-Id of the SDEV
    * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests
    * "type" is the semantic type of the resource that RAP wants to get information, it is related to the semantic description of the resource.
    * "type": "Observation", always as this.
* "type": "HISTORY", always as this.

Response from Agent:

```

[
  {
    "resourceId": "5c:cf:7f:3a:6b:76",
    "location": {
      "longitude": -2.944728,
      "latitude": 43.26701,
      "altitude": 20
    },
    "resultTime": "1970-1-1T02:00:16",
    "samplingTime": "1970-1-1T02:00:16",
    "obsValues": [
      {
        "value": "25.19",
        "obsProperty": {
          "@c": ".Property",
          "name": "temperature",
          "description": ""
        },
        "uom": {
          "@c": "UnitOfMeasurment",
          "symbol": "°C",
          "name": "°C",
          "description": ""
        }
      },
      {
        "value": "1009.31",
        "obsProperty": {
          "@c": ".Property",
          "name": "pressure",
          "description": ""
        },
        "uom": {
          "@c": "UnitOfMeasurment",
          "symbol": "mBar",
          "name": "mBar",
          "description": ""
        }
      }
    ]
  }
]

```

 The response is the same of the GET, but it is actually an array of Json like the GET response.


### RAP SUBSCRIBE

Request from RAP:

```
{
  "resourceInfo" : [ {
    "symbioteId" : "abcdefgh",
    "internalId" : "123456",
    "type" : "Light"

  }, {
    "type" : "Observation"
  } ],
  "type" : "SUBSCRIBE"
}
```

Where:

* "resourceInfo":

    * "symbioteId" is the symbiote-Id of the SDEV
    * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests
    * "type" is the semantic type of the resource that RAP wants to get information, it is related to the semantic description of the resource.
    * "type": "Observation", always as this.
* "type": "SUBSCRIBE", always as this.

Response from Agent:
It is just an HTTP 200.

 ##### RAP UNSUBSCRIBE

 Request from RAP:

 ```
  {
    "resourceInfo" : [ {
      "symbioteId" : "abcdefgh",
      "internalId" : "123456",
      "type" : "Light"

    }, {
      "type" : "Observation"
    } ],
    "type" : "UNSUBSCRIBE"
  }
 ```

 Where:

 * "resourceInfo":

     * "symbioteId" is the symbiote-Id of the SDEV
     * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests
     * "type" is the semantic type of the resource that RAP wants to get information, it is related to the semantic description of the resource.
     * "type": "Observation", always as this.
 * "type": "UNSUBSCRIBE", always as this.

 Response from Agent:
 It is just an HTTP 200.

 ##### RAP SET

 ```
  {
    "resourceInfo" : [ {
      "symbioteId" : "{symbioteId}",
      "internalId" : "{internalId}",
      "type" : "{Model}"
    } ],
    "body" : {
      "{capability}": [
        { "{restriction}": "{value}" }
      ]
    },
    "type" : "SET"
  }
 ```

 Where:

 * "resourceInfo":

     * "symbioteId" is the symbiote-Id of the SDEV
     * "internalIdResource" is the internal identifier used from the agent, it is used by the RAP to addresses requests
     * "type" is the semantic type of the resource that RAP wants to get information, it is related to the semantic description of the resource.
 * "body" contains the actuation to do on the resource:
     * "capability" is the Capability Class, as defined in the CIM (Core Information Model) https://github.com/symbiote-h2020/SymbIoTeLibraries/tree/master/src/main/java/eu/h2020/symbiote/model/cim. Inside this class there are the restriction values that represents the values to change on the resource capability.
 * "type": "SET", always as this.


 ### Modosmart API
 On startup modosmart api will scan for all available sensors and actuators and will register all of them through inkeeper interface and payload will be encrypted using LWSP.

 Later client devices could scan for those resources using the public resource endpoint to get devices with their registered Symbiote ID.

 In order for a client device to send requests to rap plugin, the requests header should include security mentioned [here](https://github.com/symbiote-h2020/SymbIoTeSecurity)

 A token should be generated from url POST ```https://symbiote-open.man.poznan.pl/coreInterface/aam/get_guest_token```

 and then later to used to create headers of requests to rap as follows
 ```
 {
   x-auth-size: 1,
   x-auth-timestamp: 1540687273277,
   x-auth-hash: 00000000000000000000,
   x-auth-1: {"token":"eyJhbGciOiJFUzI1NiJ9.eyJ0dHlwIjoiR1VFU1QiLCJzdWIiOiJndWVzdCIsImlwayI6Ik1Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERBUWNEUWdBRXQwVExQODBZUDFHWHhiVXErYkd5ZGdFZzRuNzFqVkRVTVdBYXoxbTBkam5LL0lldUlSL3lWNGNLSnZnTzlST3pMZUVNODBzbThMQ0JkTCtzYW9wdzZRPT0iLCJpc3MiOiJTeW1iSW9UZV9Db3JlX0FBTSIsImV4cCI6MTU0MTE2OTczNywiaWF0IjoxNTQxMTY5Njc3LCJqdGkiOiIxMzY0MTUxOTUiLCJzcGsiOiJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRFFnQUVhQW55RTM1K1VEcU9Md1VSdEFiTUEwWHFuR2Q4Yk9yRnk2azZhOENLSVNpMk8wSVg5Nkl6Q21BZ3FPcDg3dW90dmFFRGVIWUd4MDc1TVZjbklnVUxXZz09In0.EZ0PggqOhIwZAQn-HtYK-yWlqNtmBD4q9U2WaN7uQrpJGleoctumrLBXr1YRD3ONHYsEQkriI-NuM9Xz4H5TiQ",
    "authenticationChallenge":"",
    "clientCertificate":"",
    "clientCertificateSigningAAMCertificate":"",
    "foreignTokenIssuingAAMCertificate":""
  }
 }
 ```

 Using the rap endpoint on SSP the client can read sensor readings by sending GET request for example to ```https://symbioteweb.eu.ngrok.io/rap/Sensors('{Symbiote ID}')/Observations?$top=1```, this will essentially send a POST a request to registered interworking service url, which points to the agent implemented in the modosmart api.

Actuator could be controlled in similar steps, but by sending PUT request to ```http://symbioteweb.eu.ngrok.io/rap/Actuators('{Symbiote ID}')```
 Modosmart later will handle those requests through implemented agent and will send the response containing readings from sensors, or result from AC switch to SSP which will forward it to the client application running on mobile phone.
