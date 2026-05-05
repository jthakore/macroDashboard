from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from macro_dashboard.contracts import Observation, TimeSeriesContract
from macro_dashboard.pipeline import build_gold_outputs, initialize_project, prepare_time_series, save_time_series


class PipelineTests(unittest.TestCase):
    def test_prepare_time_series_computes_transforms(self) -> None:
        observations = [Observation(date=f"2025-{month:02d}-01", value=float(month)) for month in range(1, 13)]
        contract = TimeSeriesContract(
            series_id="TEST:GROWTH",
            series_name="Growth Test",
            bucket="Growth",
            source="Unit Test",
            observations=observations,
        )
        prepared = prepare_time_series(contract, as_of=date(2026, 1, 1))
        self.assertEqual(prepared.frequency, "monthly")
        self.assertEqual(prepared.transforms.three_month_change, 3.0)
        self.assertEqual(prepared.transforms.acceleration, "stable")
        self.assertTrue(prepared.observations[-1].is_latest)

    def test_build_outputs_creates_regime_report_and_chart_specs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data_dir = Path(tmp)
            initialize_project(data_dir)
            for series_id, bucket, start in [
                ("FRED:DGS10", "Financial conditions", 4.0),
                ("FRED:DGS2", "Financial conditions", 5.0),
                ("FRED:INDPRO", "Growth", 100.0),
                ("FRED:CPILFESL", "Inflation", 300.0),
            ]:
                observations = [
                    Observation(date=f"2024-{month:02d}-01", value=start + month)
                    for month in range(1, 13)
                ] + [
                    Observation(date=f"2025-{month:02d}-01", value=start + 12 + month)
                    for month in range(1, 13)
                ]
                save_time_series(
                    data_dir,
                    TimeSeriesContract(
                        series_id=series_id,
                        series_name=series_id,
                        bucket=bucket,
                        source="Unit Test",
                        observations=observations,
                    ),
                )
            result = build_gold_outputs(data_dir)
            self.assertGreaterEqual(result["series"], 4)
            self.assertGreaterEqual(result["chart_specs"], 1)
            self.assertTrue((data_dir / "gold" / "regime_scores" / "regime_report.json").exists())


if __name__ == "__main__":
    unittest.main()

