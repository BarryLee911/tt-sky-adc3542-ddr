# ADC3542 interface and timing assumptions

Source: [TI ADC354x datasheet SBAS840C](https://www.ti.com/lit/ds/symlink/adc3542.pdf),
pin table p4, timing p13, Figure 7-2 p26, default table at left of Figure 8-44
p49, mode initialization p51, register 0x07 p57, and power-up sequence p73.
The remapped example at the right of Figure 8-44 is not the selected mapping.

| ADC pin | ASIC pin | DCLK high | Following DCLK low |
|---|---|---|---|
| D17 (18) | ui[0] | bit0 | bit7 |
| D16 (19) | ui[1] | bit1 | bit8 |
| D15 (20) | ui[2] | bit2 | bit9 |
| D14 (21) | ui[3] | bit3 | bit10 |
| D13 (22) | ui[4] | bit4 | bit11 |
| D12 (23) | ui[5] | bit5 | bit12 |
| D11 (24) | ui[6] | bit6 | bit13 |
| DCLK (26) | ui[7] | 1 | 0 |

After supplies/reference and ADC sampling clock settle, follow the hardware
reset and approximately 200000-clock calibration sequence in the datasheet.
Program 0x07=0xA9 first, then 0x13=1, wait approximately 1ms, and 0x13=0.
The e-fuse load resets other SPI writes, so configure other features afterward.
Use the default raw, two's-complement, 14-bit mapping without DDC. This matches
the RTL default INPUT_TWOS_COMPLEMENT=1. For ADC offset binary, configure its
digital/format registers as documented and set that RTL parameter to zero;
do not convert twice. Verify constant and ramp test codes before measurement.

The source data and DCLK change near the same edges. ADC tPD from sample-clock
falling edge to DCLK rising edge is 3/5/7ns minimum/typical/maximum. At 25MSPS,
tCD lists -0.4ns minimum and -0.2ns nominal; its MAX column is blank. The nominal
number is not a guaranteed maximum. The falling edge and actual load/duty/skew
budget need separate confirmation. Level-converter data rate is not a timing
closure result. Seven data signals and DCLK require a coherent capture aperture;
independent bit synchronizers cannot fix an uncontrolled bus crossing.

Define H=24.4140625ns and capture phase PHI after the ideal half-word launch.
With earliest/latest arrivals Amin/Amax, a valid aperture must satisfy both:

```
Amax + setup + uncertainty < PHI
PHI < H + Amin - hold - uncertainty
```

The behavioural sweep assumes data-to-DCLK skew +/-1ns, falling-edge shift
+/-2ns, model setup=1ns, hold=0.5ns, and uncertainty=0.5ns. These are illustrative
bounds, not measured board or ASIC specifications. With no added common delay,
the grid's all-corner pass range is 12..23ns. With an illustrative added delay
of 3..5ns, it is 17..24ns and the modulo-H range 0..2ns. The two separated ranges
must not be joined into one continuous interval. Correct data observed inside
the excluded setup/hold guard still fails a scenario.

The files in constraints/ are an interface-fragment and an explicitly illustrative
budget. They are not automatically loaded into the official GDS build: physical
defaults and board-specific DDR signoff are distinct evidence. Never false-path
the eight ui inputs or declare DCLK an unrelated clock to make violations vanish.
Real signoff requires cell libraries, pad/slew limits, clocks after CTS, board
and translator min/max PVT delays, ADC output duty bounds and setup AND hold.

If an upper half is captured on edge C, sample_valid is registered after C;
the decimator considers it at C+1. Only every D=2^(LEVEL-1)th complete word
advances COUNT and accumulation. Since reset/reacquisition, raw zero-based
indices D-1, 2D-1, 3D-1, ... are selected. LEVEL1 selects all complete words.
A completed 16-period result reaches
the latest register at C+2 and can enter a new tag0 snapshot at C+3 or later.
Selected-sample index n starts from the first selected word; its COUNT reference is
floor((n mod 2048)/1024). ADC conversion latency and release phase still require
calibration against the physical excitation reference. Equal clock frequencies
alone do not establish absolute phase or error-free 40.96MHz operation.

Changing LEVEL does not slow the physical DDR receiver or the ADC clock. The
ADC must still emit one half-word per clk; slowing DCLK without changing the
receiver architecture is a framing error, even at a higher LEVEL. Input timing
budgets above therefore apply to every mode. Effective rates, first-result
latency, reference frequency, reset-only reconfiguration and aliasing limits
are documented in [multi-level behavior](multilevel.md).
