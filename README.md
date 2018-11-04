# [ModoSmart Symbiote](http://www.modosmart.com/)

This repository contains the Modosmart API service that should be consumed on behalf of the client by [Symbiote Smart Space](https://github.com/symbiote-h2020/SymbioteSmartSpace) to connect to Modosmart devices over BLE and WiFi.

On startup this application will scan for nearby Room Sensors and Ac Switch and will register those devices on Symbiote Core, so that later client application (mobile phone) could learn about the available devices.

### What is Symbiote
symbIoTe is an interoperable ecosystem where any IoT platform and/or resource can interact in a trusted and unified way.

symbIoTe is an Open Source middleware which allows IoT solutions providers to expose, share and exchange their resources.

For more info about Symbiote visit [Symbiote](https://www.symbiote-h2020.eu/).

### Architecture
![Architecture](https://raw.githubusercontent.com/mohamed-elsabagh/modosmart-api/master/resources/architecture.png)
