import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from weather_compression.agent import compress_with_agent, decompress_with_agent, train_agent
from weather_compression.benchmark import benchmark
from weather_compression.claude_insights import build_prompt
from weather_compression.codecs import CODECS
from weather_compression.sample import historical_weather_samples, one_day_weather_payload


class CodecTests(unittest.TestCase):
    def test_all_codecs_restore_exact_weather_payload(self) -> None:
        data = one_day_weather_payload()
        for compress, decompress in CODECS.values():
            self.assertEqual(decompress(compress(data)), data)

    def test_benchmark_verifies_every_codec(self) -> None:
        results = benchmark(one_day_weather_payload())
        self.assertEqual({result["name"] for result in results}, {"trained-weather-agent", *CODECS})
        self.assertTrue(all(result["bytes"] > 0 for result in results))

    def test_trained_agent_round_trips_and_can_be_reloaded(self) -> None:
        agent = train_agent(historical_weather_samples())
        data = one_day_weather_payload()
        compressed = compress_with_agent(data, agent)
        self.assertEqual(decompress_with_agent(compressed, agent), data)
        with TemporaryDirectory() as directory:
            artifact = Path(directory) / "agent.json"
            agent.save(artifact)
            restored_agent = type(agent).load(artifact)
        self.assertEqual(decompress_with_agent(compressed, restored_agent), data)

    def test_claude_prompt_keeps_compression_deterministic(self) -> None:
        prompt = build_prompt({"current_savings_percent": 39.1, "decode_hash_checks": "passed"})
        self.assertIn("advisory summary only", prompt)
        self.assertIn("Do not make changes to compression settings", prompt)
