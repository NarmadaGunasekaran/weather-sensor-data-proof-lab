# Weather Sensor Data Proof Lab

I built this small project to explore one question: can a combined weather packet be made smaller without changing any of its original values?

The project uses weather packets containing temperature, humidity, wind speed, and pressure. It checks that a packet can be encoded, decoded, and compared byte for byte with the original. It also compares the sensor-aware example with standard compression methods.

## Demo

The easiest place to start is `pilot-lab.html`.

It includes six small dashboard views:

- **Overview** — choose a weather gateway or weather API pipeline, process packets, and see the lossless proof.
- **Identify fields** — collect ten combined packets and label anonymous channels. The live API path uses the field names supplied by the API; unknown packets use a cautious signal-based suggestion.
- **Compare methods** — compare the compact example format with browser GZIP on the same captured packets.
- **Business impact** — simple estimates for capacity, sampling rate, and data cost.
- **Evidence report** — download a JSON summary of the validation run.

The dashboard uses synthetic data by default. Select **Weather API pipeline** and then **Load live Open-Meteo sample** to load ten real weather readings from Open-Meteo. The live sample is for demonstration only and does not send data to a production system.

## What “lossless” means here

Lossless does not mean “the values look similar.” It means the decoded packet must be exactly the same as the original packet. The demo checks this after every processed packet and safely rejects a corrupted packet.

## Python benchmark

The Python code in `src/weather_compression/` compares a trained, sensor-aware research codec with standard library codecs: `zlib`, `gzip`, `bz2`, and `lzma`.

Run the included benchmark:

```bash
PYTHONPATH=src python3 -m weather_compression.benchmark
```

Run the tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Notes

- This is a learning and proof-of-concept project, not a production compression product.
- The browser demo uses a small fixed sample window so that the workflow is easy to follow.
- A real pilot would use representative data, confirm available sensor metadata, and measure target-device and network behaviour before deployment.
