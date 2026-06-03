#!/usr/bin/env python3
"""
summarize_efficiency.py

Parse the output file `allSimulatedEfficiencies.txt` produced by the SGMC code
and produce a clean tabular summary of proton energy vs. central
efficiency with separate columns for the systematic and statistical
uncertainties.

Definitions
-----------
- Central efficiency: the median efficiency across all variants in the
  (beamSpot, threshold, stoppingFile, DeIdx) parameter scan.  This is
  what the input file labels "Central (median)".

- Systematic uncertainty (sigma_syst): the unbiased sample standard
  deviation of the efficiency across all variants at a given energy.
  This captures the spread induced by the four systematic parameters.

- Statistical uncertainty (sigma_stat): the per-variant Monte Carlo
  statistical uncertainty of the median variant, as already computed by
  the simulation as eff / sqrt(h6).  This is taken directly from the
  "Central (median)" line in the input file rather than recomputed.

The two uncertainties are reported separately rather than combined in
quadrature so the relative contribution of each can be inspected.  To
get a single combined 1-sigma error bar, add them in quadrature:
    sigma_total = sqrt(sigma_syst**2 + sigma_stat**2)

Usage
-----
    python3 summarize_efficiency.py [input_path] [output_path]

Defaults are the paths used to simulate all proton energies from 31Cl PRC
article, with N=100 protons against all combinations of lower limit,
upper limit, and expected central value for all sources of systematic
uncertainty. 
"""

import re
import sys
import statistics
from pathlib import Path

# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

DEFAULT_INPUT  = Path("results/allSimulatedEfficiencies.txt")
DEFAULT_OUTPUT = Path("results/efficiencySummaryWithUncertainties.txt")

# ---------------------------------------------------------------------------
# Regular expressions matching the relevant lines in the input file
# ---------------------------------------------------------------------------

ENERGY_RE = re.compile(
    r"^Proton energy:\s+([\d.]+)\s+MeV\s+\((\d+)\s*keV\)"
)

CENTRAL_RE = re.compile(
    r"^\s*Central\s*\(median\)\s*:\s*eff\s*=\s*([\d.]+)\s*\+/-\s*([\d.]+)"
)

# Variant rows in the "All variants:" table:
#   BeamSpot_0   192  data/...  0    100    1.0000   0.1000
# Match by anchoring on "BeamSpot_<digit>" and capturing the eff column.
VARIANT_RE = re.compile(
    r"^\s*BeamSpot_\d+\s+\d+\s+\S+\s+\d+\s+\d+\s+([\d.]+)\s+[\d.]+\s*$"
)

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_summary(path: Path):
    """Yield one dict per proton energy block in the summary file."""
    cur = None
    in_variants = False

    with path.open() as f:
        for line in f:
            m_e = ENERGY_RE.match(line)
            if m_e:
                if cur is not None:
                    yield cur
                cur = {
                    "E_MeV":    float(m_e.group(1)),
                    "E_keV":    int(m_e.group(2)),
                    "central":  None,
                    "stat":     None,
                    "variants": [],
                }
                in_variants = False
                continue

            if cur is None:
                continue

            m_c = CENTRAL_RE.match(line)
            if m_c:
                cur["central"] = float(m_c.group(1))
                cur["stat"]    = float(m_c.group(2))
                continue

            if "All variants:" in line:
                in_variants = True
                continue

            if in_variants:
                m_v = VARIANT_RE.match(line)
                if m_v:
                    cur["variants"].append(float(m_v.group(1)))

    if cur is not None:
        yield cur


def systematic_sigma(effs):
    """Unbiased sample standard deviation across variants."""
    if len(effs) < 2:
        return 0.0
    return statistics.stdev(effs)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    input_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    rows = []
    for r in parse_summary(input_path):
        rows.append({
            "E_MeV":     r["E_MeV"],
            "E_keV":     r["E_keV"],
            "central":   r["central"],
            "syst":      systematic_sigma(r["variants"]),
            "stat":      r["stat"],
            "nVariants": len(r["variants"]),
        })

    rows.sort(key=lambda x: x["E_MeV"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        f.write("# Proton-detection efficiency from SGMC simulations.\n")
        f.write("#\n")
        f.write("# Central value: median efficiency across all variants of the\n")
        f.write("#   (beamSpot, threshold, stoppingFile, DeIdx) parameter scan.\n")
        f.write("#\n")
        f.write("# +/- syst: 1-sigma sample standard deviation of the efficiency\n")
        f.write("#   across all variants at this energy.  Captures the spread\n")
        f.write("#   induced by the four systematic parameters.\n")
        f.write("#\n")
        f.write("# +/- stat: Monte Carlo statistical uncertainty of the median\n")
        f.write("#   variant, computed as eff/sqrt(h6) by the simulation.\n")
        f.write("#\n")
        f.write("# Total 1-sigma uncertainty: sqrt(syst^2 + stat^2)\n")
        f.write("#\n")
        f.write(
            f"# {'E[keV]':>7}  {'E[MeV]':>9}  {'eff':>9}  "
            f"{'+/- syst':>9}  {'+/- stat':>9}  {'nVar':>5}\n"
        )
        for row in rows:
            f.write(
                f"  {row['E_keV']:7d}  "
                f"{row['E_MeV']:9.4f}  "
                f"{row['central']:9.4f}  "
                f"{row['syst']:9.4f}  "
                f"{row['stat']:9.4f}  "
                f"{row['nVariants']:5d}\n"
            )

    print(f"Wrote {len(rows)} entries to {output_path}")
    if rows:
        print(f"Energy range: {rows[0]['E_keV']} - {rows[-1]['E_keV']} keV")


if __name__ == "__main__":
    main()
