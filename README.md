# Edge aquaconecta

Edge is a Python-based solution focused on acquiring and processing data from water sensors. Its main goal is to read water level and quality through locally connected sensors, process this data, and then send it via POST requests to a server or central system for further analysis or storage.

The project’s folder structure typically includes modules for sensor reading, data processing, and communication with external services. This enables a modular and easy-to-maintain architecture, making it simple to integrate new sensors or communication protocols in the future.

In summary, Edge automates the collection and transmission of relevant water information, optimizing management and real-time monitoring at the network edge.

## Main Features

- Local acquisition of water sensor data (level and quality)
- Modular and scalable architecture
- Easy integration and extension
- Automated data transmission to remote services

## Installation

```bash
pip install edge-aquaconecta
```
## Run 
```Run
 flask run --host=0.0.0.0 --port=5001
 lt --port 5001        
