"""Generate England provider files in Synthea's provider CSV format.

- uk_hospitals.csv:   real NHS acute hospitals with A&E (approximate coordinates, no street address)
- uk_gp_practices.csv: synthetic GP practices, two per place in uk_zipcodes.csv
- uk_urgent_care.csv:  synthetic urgent treatment centres, one per place

Phone numbers use Ofcom's reserved drama range (01632 960xxx) so none are real.
The 'id' column is numeric so Synthea generates a valid-format NPI from it.
"""
import csv
import math
import sys

STATE = "England"
HEADER = ["id", "provider_num", "name", "address", "city", "state", "zip", "lat", "lon",
          "phone", "provider_type_code", "emergency"]

# name, town, lat, lon
HOSPITALS = [
    # London
    ("St Thomas' Hospital", "London", 51.4985, -0.1188),
    ("Royal London Hospital", "London", 51.5189, -0.0590),
    ("King's College Hospital", "London", 51.4682, -0.0938),
    ("St Mary's Hospital", "London", 51.5173, -0.1738),
    ("University College Hospital", "London", 51.5246, -0.1357),
    ("Royal Free Hospital", "London", 51.5532, -0.1655),
    ("St George's Hospital", "London", 51.4270, -0.1745),
    ("Charing Cross Hospital", "London", 51.4870, -0.2190),
    ("Chelsea and Westminster Hospital", "London", 51.4844, -0.1818),
    ("Northwick Park Hospital", "Harrow", 51.5755, -0.3218),
    ("Croydon University Hospital", "Croydon", 51.3896, -0.1060),
    ("Queen's Hospital", "Romford", 51.5689, 0.1789),
    ("Whipps Cross Hospital", "London", 51.5779, 0.0010),
    ("North Middlesex University Hospital", "London", 51.6131, -0.0721),
    ("Hillingdon Hospital", "Uxbridge", 51.5263, -0.4615),
    ("West Middlesex University Hospital", "Isleworth", 51.4740, -0.3245),
    ("Kingston Hospital", "Kingston upon Thames", 51.4146, -0.2836),
    ("Princess Royal University Hospital", "Orpington", 51.3672, 0.0546),
    ("Queen Elizabeth Hospital Woolwich", "London", 51.4795, 0.0563),
    ("Homerton University Hospital", "London", 51.5469, -0.0447),
    ("Newham University Hospital", "London", 51.5226, 0.0353),
    ("Ealing Hospital", "Southall", 51.5072, -0.3463),
    ("Barnet Hospital", "Barnet", 51.6499, -0.2140),
    ("University Hospital Lewisham", "London", 51.4528, -0.0168),
    ("St Helier Hospital", "Carshalton", 51.3810, -0.1846),
    # North East
    ("Royal Victoria Infirmary", "Newcastle upon Tyne", 54.9799, -1.6202),
    ("Sunderland Royal Hospital", "Sunderland", 54.9030, -1.4130),
    ("Queen Elizabeth Hospital Gateshead", "Gateshead", 54.9420, -1.5760),
    ("South Tyneside District Hospital", "South Shields", 54.9840, -1.4350),
    ("Northumbria Specialist Emergency Care Hospital", "Cramlington", 55.0950, -1.5800),
    ("James Cook University Hospital", "Middlesbrough", 54.5520, -1.2140),
    ("University Hospital of North Tees", "Stockton-on-Tees", 54.5750, -1.3240),
    ("Darlington Memorial Hospital", "Darlington", 54.5300, -1.5640),
    ("University Hospital of North Durham", "Durham", 54.7870, -1.5950),
    # North West
    ("Manchester Royal Infirmary", "Manchester", 53.4626, -2.2253),
    ("Salford Royal Hospital", "Salford", 53.4870, -2.3220),
    ("Royal Bolton Hospital", "Bolton", 53.5560, -2.4370),
    ("Royal Oldham Hospital", "Oldham", 53.5530, -2.1230),
    ("Stepping Hill Hospital", "Stockport", 53.3820, -2.1350),
    ("Royal Albert Edward Infirmary", "Wigan", 53.5580, -2.6450),
    ("Fairfield General Hospital", "Bury", 53.5960, -2.2670),
    ("Wythenshawe Hospital", "Manchester", 53.3880, -2.2930),
    ("Tameside General Hospital", "Ashton-under-Lyne", 53.4930, -2.0770),
    ("Royal Liverpool University Hospital", "Liverpool", 53.4100, -2.9660),
    ("Aintree University Hospital", "Liverpool", 53.4680, -2.9330),
    ("Arrowe Park Hospital", "Birkenhead", 53.3700, -3.0960),
    ("Whiston Hospital", "Prescot", 53.4200, -2.7900),
    ("Southport and Formby District General Hospital", "Southport", 53.6290, -2.9930),
    ("Royal Preston Hospital", "Preston", 53.7910, -2.7060),
    ("Royal Blackburn Teaching Hospital", "Blackburn", 53.7320, -2.4660),
    ("Blackpool Victoria Hospital", "Blackpool", 53.8210, -3.0130),
    ("Royal Lancaster Infirmary", "Lancaster", 54.0420, -2.7990),
    ("Warrington Hospital", "Warrington", 53.3930, -2.6080),
    ("Countess of Chester Hospital", "Chester", 53.2120, -2.9000),
    ("Leighton Hospital", "Crewe", 53.1100, -2.4770),
    ("Cumberland Infirmary", "Carlisle", 54.8950, -2.9560),
    # Yorkshire and the Humber
    ("Leeds General Infirmary", "Leeds", 53.8020, -1.5520),
    ("St James's University Hospital", "Leeds", 53.8070, -1.5200),
    ("Bradford Royal Infirmary", "Bradford", 53.8070, -1.7950),
    ("Pinderfields Hospital", "Wakefield", 53.6950, -1.4900),
    ("Huddersfield Royal Infirmary", "Huddersfield", 53.6550, -1.8150),
    ("Calderdale Royal Hospital", "Halifax", 53.7050, -1.8680),
    ("Northern General Hospital", "Sheffield", 53.4080, -1.4580),
    ("Doncaster Royal Infirmary", "Doncaster", 53.5300, -1.1080),
    ("Rotherham Hospital", "Rotherham", 53.4130, -1.3330),
    ("Barnsley Hospital", "Barnsley", 53.5590, -1.5000),
    ("Hull Royal Infirmary", "Kingston upon Hull", 53.7440, -0.3570),
    ("York Hospital", "York", 53.9690, -1.0860),
    ("Harrogate District Hospital", "Harrogate", 53.9930, -1.5600),
    ("Scarborough Hospital", "Scarborough", 54.2750, -0.4250),
    ("Diana Princess of Wales Hospital", "Grimsby", 53.5520, -0.0850),
    ("Scunthorpe General Hospital", "Scunthorpe", 53.5800, -0.6630),
    # East Midlands
    ("Queen's Medical Centre", "Nottingham", 52.9440, -1.1860),
    ("King's Mill Hospital", "Sutton-in-Ashfield", 53.1310, -1.2170),
    ("Leicester Royal Infirmary", "Leicester", 52.6270, -1.1360),
    ("Royal Derby Hospital", "Derby", 52.9100, -1.5170),
    ("Chesterfield Royal Hospital", "Chesterfield", 53.2490, -1.3910),
    ("Northampton General Hospital", "Northampton", 52.2350, -0.8820),
    ("Lincoln County Hospital", "Lincoln", 53.2350, -0.5200),
    ("Pilgrim Hospital", "Boston", 52.9930, -0.0080),
    # West Midlands
    ("Queen Elizabeth Hospital Birmingham", "Birmingham", 52.4530, -1.9420),
    ("Heartlands Hospital", "Birmingham", 52.4790, -1.8280),
    ("University Hospital Coventry", "Coventry", 52.4210, -1.4400),
    ("New Cross Hospital", "Wolverhampton", 52.6000, -2.0960),
    ("Walsall Manor Hospital", "Walsall", 52.5840, -2.0010),
    ("Russells Hall Hospital", "Dudley", 52.5050, -2.1060),
    ("Sandwell General Hospital", "West Bromwich", 52.5300, -1.9830),
    ("Royal Stoke University Hospital", "Stoke-on-Trent", 53.0040, -2.2120),
    ("County Hospital Stafford", "Stafford", 52.8240, -2.1180),
    ("Worcestershire Royal Hospital", "Worcester", 52.1900, -2.1810),
    ("Hereford County Hospital", "Hereford", 52.0610, -2.7080),
    ("Princess Royal Hospital", "Telford", 52.7040, -2.5110),
    ("Royal Shrewsbury Hospital", "Shrewsbury", 52.7090, -2.7960),
    ("George Eliot Hospital", "Nuneaton", 52.5130, -1.4520),
    # East of England
    ("Norfolk and Norwich University Hospital", "Norwich", 52.6190, 1.2200),
    ("Queen Elizabeth Hospital King's Lynn", "King's Lynn", 52.7560, 0.4470),
    ("Addenbrooke's Hospital", "Cambridge", 52.1750, 0.1400),
    ("Peterborough City Hospital", "Peterborough", 52.5850, -0.2800),
    ("Luton and Dunstable University Hospital", "Luton", 51.8950, -0.4740),
    ("Bedford Hospital", "Bedford", 52.1280, -0.4680),
    ("Ipswich Hospital", "Ipswich", 52.0610, 1.1890),
    ("Colchester General Hospital", "Colchester", 51.9100, 0.8990),
    ("Broomfield Hospital", "Chelmsford", 51.7740, 0.4660),
    ("Southend University Hospital", "Southend-on-Sea", 51.5530, 0.6860),
    ("Basildon University Hospital", "Basildon", 51.5580, 0.4510),
    ("Watford General Hospital", "Watford", 51.6500, -0.4040),
    ("Lister Hospital", "Stevenage", 51.9270, -0.2140),
    # South East
    ("Royal Sussex County Hospital", "Brighton", 50.8190, -0.1180),
    ("Eastbourne District General Hospital", "Eastbourne", 50.7860, 0.2690),
    ("Conquest Hospital", "Hastings", 50.8770, 0.5650),
    ("East Surrey Hospital", "Redhill", 51.2190, -0.1640),
    ("Worthing Hospital", "Worthing", 50.8170, -0.3600),
    ("Southampton General Hospital", "Southampton", 50.9330, -1.4330),
    ("Queen Alexandra Hospital", "Portsmouth", 50.8500, -1.0700),
    ("Basingstoke and North Hampshire Hospital", "Basingstoke", 51.2780, -1.1160),
    ("St Mary's Hospital Newport", "Newport", 50.7110, -1.3000),
    ("Royal Berkshire Hospital", "Reading", 51.4500, -0.9600),
    ("Wexham Park Hospital", "Slough", 51.5320, -0.5770),
    ("John Radcliffe Hospital", "Oxford", 51.7640, -1.2190),
    ("Milton Keynes University Hospital", "Milton Keynes", 52.0260, -0.7360),
    ("Stoke Mandeville Hospital", "Aylesbury", 51.7990, -0.8070),
    ("Royal Surrey County Hospital", "Guildford", 51.2410, -0.6090),
    ("St Peter's Hospital", "Chertsey", 51.3770, -0.5280),
    ("Maidstone Hospital", "Maidstone", 51.2730, 0.4840),
    ("Kent and Canterbury Hospital", "Canterbury", 51.2650, 1.0850),
    ("Medway Maritime Hospital", "Gillingham", 51.3790, 0.5450),
    ("Queen Elizabeth The Queen Mother Hospital", "Margate", 51.3780, 1.3920),
    # South West
    ("Bristol Royal Infirmary", "Bristol", 51.4590, -2.5960),
    ("Southmead Hospital", "Bristol", 51.4960, -2.5920),
    ("Royal United Hospital", "Bath", 51.3920, -2.3900),
    ("Weston General Hospital", "Weston-super-Mare", 51.3230, -2.9720),
    ("Musgrove Park Hospital", "Taunton", 51.0110, -3.1210),
    ("Derriford Hospital", "Plymouth", 50.4170, -4.1130),
    ("Royal Devon and Exeter Hospital", "Exeter", 50.7170, -3.5060),
    ("Torbay Hospital", "Torquay", 50.4780, -3.5450),
    ("Royal Cornwall Hospital", "Truro", 50.2670, -5.0930),
    ("Royal Bournemouth Hospital", "Bournemouth", 50.7470, -1.8240),
    ("Gloucestershire Royal Hospital", "Gloucester", 51.8660, -2.2300),
    ("Cheltenham General Hospital", "Cheltenham", 51.8970, -2.0710),
    ("Great Western Hospital", "Swindon", 51.5410, -1.7350),
    ("Salisbury District Hospital", "Salisbury", 51.0480, -1.7930),
]

# Small fixed offsets (degrees, roughly 0.5-1 km) so a place's GP practices aren't stacked
GP_SITES = [("Health Centre", 0.006, -0.008), ("Medical Practice", -0.005, 0.009)]


class Phones:
    def __init__(self):
        self.n = 0

    def next(self):
        if self.n > 999:
            raise SystemExit("ran out of 01632 960xxx drama-range numbers")
        number = f"01632960{self.n:03d}"
        self.n += 1
        return number


def nearest_postcode(places, lat, lon):
    def dist(p):
        dlat = p["LAT"] - lat
        dlon = (p["LON"] - lon) * math.cos(math.radians(lat))
        return dlat * dlat + dlon * dlon
    return min(places, key=dist)["ZCTA5"]


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


def main(zipcodes_path, out_dir):
    with open(zipcodes_path, newline="", encoding="utf-8") as f:
        places = [dict(r, LAT=float(r["LAT"]), LON=float(r["LON"])) for r in csv.DictReader(f)]

    phones = Phones()

    names = [h[0] for h in HOSPITALS]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise SystemExit(f"duplicate hospital names: {dupes}")

    hospitals = []
    for i, (name, town, lat, lon) in enumerate(HOSPITALS, start=1):
        hospitals.append([100000 + i, f"UKH{i:04d}", name.upper(), "", town.upper(), STATE,
                          nearest_postcode(places, lat, lon), lat, lon, phones.next(),
                          "00-01", "true"])

    gps = []
    for i, p in enumerate(places):
        for j, (suffix, dlat, dlon) in enumerate(GP_SITES):
            n = i * len(GP_SITES) + j + 1
            gps.append([200000 + n, f"UKG{n:04d}", f"{p['NAME']} {suffix}".upper(), "",
                        p["NAME"].upper(), STATE, p["ZCTA5"],
                        round(p["LAT"] + dlat, 4), round(p["LON"] + dlon, 4), phones.next(),
                        "00-04", "false"])

    utcs = []
    for i, p in enumerate(places, start=1):
        utcs.append([300000 + i, f"UKU{i:04d}", f"{p['NAME']} Urgent Treatment Centre".upper(),
                     "", p["NAME"].upper(), STATE, p["ZCTA5"],
                     round(p["LAT"] - 0.004, 4), round(p["LON"] - 0.004, 4), phones.next(),
                     "12-70", "false"])

    write(f"{out_dir}/uk_hospitals.csv", hospitals)
    write(f"{out_dir}/uk_gp_practices.csv", gps)
    write(f"{out_dir}/uk_urgent_care.csv", utcs)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
