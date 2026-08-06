# Weather API Lossless Compression Report

Original payload: **1,177 bytes**  
SHA-256: `40993b86b86cc4b5cc147d5b0cc381f75c25cf16677ad3f44244d54367d1e286`

| Codec | Compressed bytes | Ratio | Saved | Compress | Decompress | Exact round trip |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| trained-weather-agent | 415 | 0.353x | 64.7% | 0.30 ms | 0.22 ms | yes |
| zlib-9 | 424 | 0.360x | 64.0% | 0.02 ms | 0.00 ms | yes |
| gzip-9 | 436 | 0.370x | 63.0% | 0.01 ms | 0.01 ms | yes |
| bz2-9 | 472 | 0.401x | 59.9% | 0.14 ms | 0.04 ms | yes |
| lzma-9 | 476 | 0.404x | 59.6% | 8.07 ms | 0.64 ms | yes |
| adaptive-predictor | 597 | 0.507x | 49.3% | 0.65 ms | 0.59 ms | yes |

`trained-weather-agent` follows a train-once, compress-anywhere workflow: a fixed prediction profile is learned from seven historical samples, then used at runtime. All methods preserve raw input bytes.