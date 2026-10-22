# Versioned TinyTapeout viewer deployment

This is an artifact deployment branch. RTL remains on `codex/ddr-multilevel`,
PR #1. This branch runs no GDS synthesis or RTL changes.

The workflow downloads the exact completed official submissions, verifies their
source commit and OAS SHA256, and deploys their original GDS/OAS models through
the official TinyTapeout viewer. The original root model remains available;
ADC3543 80MHz is added at `/adc3543-80mhz/` with its own provenance/status page.

The 80MHz layout is viewable but has worst SS setup slack -2.187ns and is not
closed across all PVT corners. The external DDR model also lacks positive margin.
