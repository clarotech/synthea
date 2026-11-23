# Synthea – UK variant

This is a fork of [Synthea](https://github.com/synthetichealth/synthea) localised to
England. `src/main/resources/synthea.properties` points at UK data instead of the
upstream US data. Outstanding work is tracked in [`todo.md`](todo.md).

## Running

```
run_synthea -p 10 -s 42            # Windows: run.bat / .\gradlew.bat run --args="-p 10 -s 42"
```

- The default state is `England` (`Generator.DEFAULT_STATE`), and it's the only state
  in the UK data. Passing a US state fails.
- Settings can be overridden per run, e.g. `--exporter.baseDirectory=<dir>`.
- `run.bat` deletes `./output` before each run.

## UK data generator scripts (`scripts/uk/`)

Several UK data files are **generated** by these scripts. Edit the tables in the
script and regenerate; don't hand-edit the output CSVs. Run them in this order,
because each one reads the previous one's output:

| Script | Output | Contents |
|---|---|---|
| `make_uk_demographics.py` | `geography/uk_demographics.csv` | 151 English places (London boroughs plus towns and cities): approximate Census 2021 population, ethnicity, and age/income/education profiles |
| `make_uk_zipcodes.py` | `geography/uk_zipcodes.csv` | One postcode district (outward code) and town-centre lat/lon per place. Fails if a place is missing from either list. |
| `make_uk_providers.py` | `providers/uk_hospitals.csv`, `uk_gp_practices.csv`, `uk_urgent_care.csv` | 141 real NHS acute hospitals with A&E; synthetic GP practices (2 per place) and urgent treatment centres (1 per place) |

From the repo root (paths are relative to `src/main/resources`):

```
python scripts/uk/make_uk_demographics.py src/main/resources/geography/uk_demographics.csv
python scripts/uk/make_uk_zipcodes.py     src/main/resources/geography/uk_demographics.csv src/main/resources/geography/uk_zipcodes.csv
python scripts/uk/make_uk_providers.py    src/main/resources/geography/uk_zipcodes.csv src/main/resources/providers
```

The scripts are deterministic: rerunning them unchanged reproduces the committed files
byte for byte. If you add a place, add it to **both** `make_uk_demographics.py` and
`make_uk_zipcodes.py`.

Conventions in the generated files:
- `STNAME`/`state` is always `England`, and the abbreviation is `ENG`.
- Phone numbers use Ofcom's drama range (`01632 960xxx`), so none are real.
- Provider `id` is numeric so Synthea can generate an NPI from it (hospitals 100000+,
  GPs 200000+, UTCs 300000+). `provider_num` holds placeholder codes (`UKH`/`UKG`/`UKU`),
  not real ODS codes.

## Hand-maintained UK files (not generated)

- `providers/uk_hospices.csv`: `state` = `England`; `provider_num` holds the ODS code
  and `npi` the CQC-style ID.
- `payers/uk_insurance_companies.csv`, `uk_insurance_plans.csv`,
  `uk_insurance_eligibilities.csv`: the NHS as the single government payer, covering
  everyone at no cost. The plan's `Default Coinsurance` must be `1.0` (payer pays 100%).
  Because of `InsurancePlan.java:172`, `0` would make the patient pay.
- `geography/timezones.csv`: has an added `England,ENG,...` row.
- `geography/uk_foreign_birthplace.json`, `uk_language_lookup.json`.

## Gotchas

- State abbreviations come from the zipcodes file (`USPS`/`ST` columns), not
  `timezones.csv`. A state missing from it causes a NullPointerException in
  `PayerManager.loadPayers`.
- `payers/eligibility_input_files/ssd_eligibility.csv` is US data, but
  `LifecycleModule.java:102` reads it on every run. Don't delete it.
- Visit types with no matching provider (nursing homes, home health) fall back to the
  nearest hospital (`generate.providers.default_to_hospital_on_failure = true`).
- The test suite is currently broken: most tests expect US (Massachusetts) data, and
  the US demographics, zipcodes and provider files have been removed. See `todo.md`.
- Shell: Windows. In PowerShell, pass a commit message with `git commit -F <file>`;
  piping a here-string to `-F -` doesn't work.
