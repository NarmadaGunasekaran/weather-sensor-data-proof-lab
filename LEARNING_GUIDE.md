# How This Project Works, in Plain English

This is a small engineering demonstration. Its goal is to send a day of weather data using fewer bytes, **without changing or losing anything**.

## First: three words you need

- **Data**: the weather API response, for example temperature and humidity for every hour.
- **Compression**: a way of writing the same data with fewer bytes.
- **Lossless**: after decompression, the result is exactly the original data. Not “almost the same”; every character and number is restored.

Think of lossless compression like abbreviating a repeated sentence. If both sides know the same rules, `T+18` can stand for a longer phrase. The receiver expands it back perfectly.

## The Bitteiler-style workflow in this project

### 1. Train once

The program looks at seven earlier one-day weather responses. It makes a small lookup table that answers this question:

> “After I have seen these two bytes, which byte is most likely to appear next?”

For example, JSON contains repeated pieces such as `"temperature_2m"`, timestamps, commas, and brackets. The training step learns common next characters in those repeating patterns.

The trained lookup table is the **compression agent**. You can save it with:

```bash
PYTHONPATH=src python3 -m weather_compression.train_agent --output weather-agent.json
```

`weather-agent.json` is a portable description of the learned rules. In a real company, this is where you would train using genuine historical sensor samples and metadata such as sensor type, sampling rate, unit, and hardware limits.

### 2. Compress at runtime

When new daily weather data arrives, the encoder reads it from left to right. For each byte it:

1. asks the trained agent for a prediction;
2. calculates the numerical difference between the prediction and the actual byte;
3. stores that difference instead of the full byte;
4. uses a standard entropy compressor to shrink the differences further.

This does **not** remove any measurements. A wrong prediction is safe because the exact difference is kept.

### 3. Reconstruct exactly

The decoder has the same trained agent. It reads each stored difference and:

1. makes the same prediction;
2. adds the stored difference back;
3. recovers the exact original byte.

The compressed file includes an agent fingerprint. If someone tries to decode with the wrong trained agent, the program stops with an error instead of returning untrustworthy data.

## What to say in an interview

> “I built a proof of concept for fully lossless weather API compression. It has a separate training phase that learns repeating patterns from historical data, then uses a fixed profile at runtime. I compare it with zlib, gzip, bz2, and lzma, and verify every method by decompressing and checking an exact SHA-256 hash.”

Be accurate: this is **inspired by** Bitteiler’s train-once / encode-inline / decode-exactly architecture. It is not Bitteiler’s proprietary system, and its learning model is deliberately simple and auditable so the project can explain the core idea.

## How to demonstrate it

1. Open `index.html` to tell the story visually.
2. Run the benchmark command below to show a real comparison.
3. Point to the `tests/` folder: it proves that decompression returns the original bytes.

```bash
PYTHONPATH=src python3 -m weather_compression.benchmark
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## A useful honest conclusion

On the included demo payload, the trained agent wins by 9 bytes over `zlib` (415 bytes vs 424 bytes). That is promising, not a universal claim: a good engineering benchmark reports results from representative real data before choosing a production method. The next professional step is to test a larger, real dataset.
