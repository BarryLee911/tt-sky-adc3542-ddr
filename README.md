# ADC3542 native DDR receiver for TinyTapeout SKY130

[![gds](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/gds.yaml/badge.svg)](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/gds.yaml)
[![test](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/test.yaml/badge.svg)](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/test.yaml)
[![ddr-regression](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/ddr-regression.yaml/badge.svg)](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/ddr-regression.yaml)
[![docs](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/docs.yaml/badge.svg)](https://github.com/BarryLee911/tt-sky-adc3542-ddr/actions/workflows/docs.yaml)

Created using the official [TinyTapeout SKY130 Verilog template](https://github.com/TinyTapeout/ttsky-verilog-template).
The official GDS, precheck, gate-level test and documentation workflows are retained.
Target: **6x2 tiles, 40.96MHz core clock, 20.48MS/s ADC, LEVEL=1..23**.

Seven data pads plus DCLK reconstruct every full 14-bit ADC word inside the ASIC.
The previous COUNT algorithm and three-fragment 27-bit output protocol are retained.
The 29-bit moving sum is divided by four only after full 14-bit accumulation.
Default ADC input format is two's complement; no external FPGA data bridge is required.

LEVEL controls processing after complete-word assembly. For LEVEL=L, select every
2^(L-1)th ADC word: the effective rate is clk/2^L. The ADC stream and receiver
remain at full rate in every mode. LEVEL0 and LEVEL24..31 are rejected. See
[multi-level behavior and validation](docs/multilevel.md) before changing modes.

本仓库从官方模板创建并公开。原8位、12位原型和上一轮本地交付均保留；新仓库仅增加
平台顶层封装、便携测试与官方构建配置。40.96MHz是构建目标，实际ADC/电平转换/PCB
采样相位仍需独立签核，不能用流程绿灯或频率比代替接口时序保证。

- [Project datasheet / pin protocol](docs/info.md)
- [Wiring, initialization and timing assumptions](docs/interface-and-timing.md)
- [Original local functional evidence](docs/local-validation-summary.json)
- [Template and preserved-source provenance](build_provenance.json)

## Tests

The official `test` and `gl_test` jobs run the same pin-level cocotb test, including
full-scale 27-bit output, midpoint input, TYPE/OE handoff, framing-error invalidation
and reset. Gate-level functional simulation deliberately uses a slow settling clock.

The additional full regression checks all 23 real divider intervals (including
two actual LEVEL23 terminal events without counter preloading), independent
full-window references at LEVEL1/2/3/5, exhaustive bit order, random/boundary codes,
both code formats, independent integer COUNT and sums, frame atomicity, recovery,
and 3969 source-synchronous timing-model combinations. A reviewable artificial
stimulus generator recreates byte-identical prior clean and combined-interference
codes, checked against hashes in test/fixtures/manifest.json. No opaque fixture
archives or measured participant data are published. These are arithmetic tests, not
new ADC noise, physiological-time or human impedance performance measurements.

With Python 3.12+ and Icarus installed:

```
pip install -r tools/requirements.txt
python tools/run_tests.py prepare
python tools/run_tests.py compile
python tools/run_tests.py run
python tools/timing_sweep.py compile
python tools/timing_sweep.py run
python tools/host_protocol.py
```

For the official cocotb harness, install test/requirements.txt, then run `make` in
test/ and verify results.xml with `python -m cocotb_tools.check_results results.xml`.
New logs/reports live in ignored build/ and GitHub Actions artifacts. No original
workspace paths, credentials, paper sources, vendor PDFs or raw study data are needed.

The ASIC flow uses the official template's standard I/O assumptions; even a successful
GDS build does not sign off the external ADC DDR aperture. Read timing reports and
the documented physical limitations before making any high-speed hardware claim.
