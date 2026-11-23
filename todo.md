# UK Synthea – outstanding work

Follow-up items raised while localising Synthea to England
(branch `uk-geography-nhs-providers`, commit `6e099fb8`).

## Tests

- [ ] **Fix the test suite.** About 25 test classes use
  `Config.get("test_state.default", "Massachusetts")` and read
  `src/main/resources/synthea.properties`, which now points at England-only data.
  The US `demographics.csv`, `zipcodes.csv` and provider files have been deleted, so
  either:
  - restore the US files under `src/test/resources` and add a test-only
    `synthea.properties` that points at them, or
  - set `test_state.default = England` and rewrite the US-specific tests.
- [ ] `PayerTest`, `PlanFinderTest` and `LossOfCareHealthRecordTest` reference
  `payers/insurance_*.csv` and the Medicaid eligibility files directly. These were
  kept, but the tests will need reviewing once the approach above is decided.

## Demographics (`geography/uk_demographics.csv`)

- [ ] Replace the approximate starter data with real ONS figures (Census 2021 /
  mid-year estimates) for every local authority, ideally from a generator script.
- [ ] Add Scotland, Wales and Northern Ireland (currently England only).
- [ ] Review the mapping of UK categories onto Synthea's US columns:
  - ethnicity: Mixed and Other go in `OTHER`; `HISPANIC` and `NATIVE` are 0
  - education: none/Level 1 → `LESS_THAN_HS`, Level 2/apprenticeship →
    `HS_DEGREE`, Level 3 → `SOME_COLLEGE`, Level 4+ → `BS_DEGREE`
  - the column named `POPESTIMATE2015` holds 2021 figures
  - each place is a local authority labelled by its main town (e.g. "Truro" = Cornwall)
- [ ] Convert the income thresholds to GBP: income bands are read as £ thousands,
  but `generate.demographics.socioeconomic.income.poverty = 17550` and
  `...income.high = 75000` are still US dollar figures.

## Postcodes (`geography/uk_zipcodes.csv`)

- [ ] Use real postcode data. Currently there's one outward code (e.g. `LS1`) and one
  town-centre point per place, so everyone in a place shares a postcode.

## Social determinants of health

- [ ] Add England rows to `geography/sdoh.csv` (or a UK equivalent). There are none
  now, so Synthea falls back to average values.

## Providers

- [ ] Replace the placeholder `provider_num` values (`UKH`/`UKG`/`UKU` + number) in
  `uk_hospitals.csv`, `uk_gp_practices.csv` and `uk_urgent_care.csv` with real NHS
  ODS codes.
- [ ] Check the hospital list against NHS data. Names and coordinates were written
  from memory; not every site may still have a full A&E (e.g. Kent and Canterbury).
- [ ] Add hospital street addresses (currently blank).
- [ ] Consider real GP practices and urgent treatment centres. The current ones are
  synthetic, two GP practices and one UTC per place.
- [ ] Add UK nursing homes (SNF) and home health providers. Config still points at US
  files, so these visits fall back to the nearest hospital.
- [ ] Review the other provider files that are still US: `longterm.csv`, `rehab.csv`,
  `dialysis.csv`, `va_facilities.csv`, `ihs_facilities.csv`, `ihs_centers.csv`.
- [ ] `uk_hospices.csv`: the `npi` column now holds the CQC-style IDs
  (`1-2846317213`), so exporters that write an NPI identifier will output those.
  Decide what should go there.

## Payers / NHS

- [ ] Optionally stop the FHIR exporters writing `Coverage`, `Claim` and
  `ExplanationOfBenefit` resources, since the UK has no payer concept (the NHS is
  modelled as a single free payer).

## Code and config tidy-up

- [ ] `Location.java:343` – the comment still says it falls back to "some random US
  location".
- [ ] `synthea.properties:142` – `generate.geography.passport_uri` is still
  `passport-USA`.
- [ ] `ClinicianSpecialty.java:9` – the javadoc references the deleted
  `providers/primary_care_facilities.csv`.
- [ ] Patient street addresses are US-style fake addresses
  (e.g. "748 Price Underpass Suite 3").

## Tooling

- [x] Add the generator scripts (`make_uk_demographics.py`, `make_uk_zipcodes.py`,
  `make_uk_providers.py`) to the repo: now in `scripts/uk/`, documented in `CLAUDE.md`.

## Git

- [ ] Open a pull request for `uk-geography-nhs-providers`:
  https://github.com/clarotech/synthea/pull/new/uk-geography-nhs-providers
