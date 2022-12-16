# Light-Swarm-Node-Red
Light Swarm Node Red Project

Communication Path:
Node MCU --> Raspberry Pi --> Node Red

1. All NodeMCUs have light sensors connected to it and they send msgs to decide the Master amongst themselves.
2. The Master then sends its data to Raspberry Pi which acts as Server. 
3. In Raspberry Pi, data logging is done and it sends the master's data to MQTT Broker.
4. MQTT client subscribes from the broker for the msgs and graphs the received data.

