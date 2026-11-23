"""Generate uk_zipcodes.csv in Synthea's zipcodes.csv format (,USPS,ST,NAME,ZCTA5,LAT,LON).

One row per place in uk_demographics.csv: approximate postcode district (outward code)
and approximate town-centre coordinates.
"""
import csv
import sys

STATE, ABBR = "England", "ENG"

PLACES = {
    # Greater London
    "Barking and Dagenham": ("IG11", 51.539, 0.081),
    "Barnet": ("NW4", 51.583, -0.226),
    "Bexley": ("DA6", 51.457, 0.150),
    "Brent": ("HA9", 51.559, -0.282),
    "Bromley": ("BR1", 51.406, 0.015),
    "Camden": ("NW1", 51.539, -0.142),
    "City of London": ("EC2", 51.515, -0.092),
    "Croydon": ("CR0", 51.372, -0.099),
    "Ealing": ("W5", 51.513, -0.305),
    "Enfield": ("EN1", 51.652, -0.081),
    "Greenwich": ("SE10", 51.482, -0.009),
    "Hackney": ("E8", 51.545, -0.055),
    "Hammersmith and Fulham": ("W6", 51.492, -0.223),
    "Haringey": ("N22", 51.597, -0.110),
    "Harrow": ("HA1", 51.580, -0.334),
    "Havering": ("RM1", 51.575, 0.183),
    "Hillingdon": ("UB8", 51.546, -0.479),
    "Hounslow": ("TW3", 51.468, -0.361),
    "Islington": ("N1", 51.538, -0.103),
    "Kensington and Chelsea": ("W8", 51.501, -0.193),
    "Kingston upon Thames": ("KT1", 51.412, -0.300),
    "Lambeth": ("SW9", 51.462, -0.115),
    "Lewisham": ("SE13", 51.462, -0.012),
    "Merton": ("SM4", 51.402, -0.195),
    "Newham": ("E15", 51.541, 0.003),
    "Redbridge": ("IG1", 51.559, 0.070),
    "Richmond upon Thames": ("TW9", 51.461, -0.303),
    "Southwark": ("SE15", 51.474, -0.069),
    "Sutton": ("SM1", 51.361, -0.193),
    "Tower Hamlets": ("E1", 51.519, -0.060),
    "Waltham Forest": ("E17", 51.583, -0.020),
    "Wandsworth": ("SW18", 51.457, -0.192),
    "Westminster": ("SW1", 51.497, -0.137),
    # North East
    "Newcastle upon Tyne": ("NE1", 54.978, -1.617),
    "Sunderland": ("SR1", 54.906, -1.381),
    "Gateshead": ("NE8", 54.952, -1.603),
    "South Shields": ("NE33", 54.999, -1.432),
    "North Shields": ("NE29", 55.009, -1.449),
    "Middlesbrough": ("TS1", 54.574, -1.235),
    "Stockton-on-Tees": ("TS18", 54.564, -1.312),
    "Darlington": ("DL1", 54.524, -1.553),
    "Hartlepool": ("TS24", 54.686, -1.212),
    "Durham": ("DH1", 54.776, -1.575),
    "Morpeth": ("NE61", 55.168, -1.689),
    # North West
    "Manchester": ("M1", 53.480, -2.242),
    "Salford": ("M5", 53.488, -2.290),
    "Bolton": ("BL1", 53.578, -2.429),
    "Oldham": ("OL1", 53.541, -2.112),
    "Rochdale": ("OL16", 53.616, -2.155),
    "Stockport": ("SK1", 53.408, -2.149),
    "Wigan": ("WN1", 53.545, -2.632),
    "Bury": ("BL9", 53.593, -2.298),
    "Altrincham": ("WA14", 53.387, -2.349),
    "Ashton-under-Lyne": ("OL6", 53.489, -2.098),
    "Liverpool": ("L1", 53.408, -2.991),
    "Birkenhead": ("CH41", 53.393, -3.014),
    "St Helens": ("WA10", 53.454, -2.737),
    "Southport": ("PR8", 53.647, -3.005),
    "Preston": ("PR1", 53.763, -2.703),
    "Blackburn": ("BB1", 53.749, -2.483),
    "Blackpool": ("FY1", 53.817, -3.054),
    "Burnley": ("BB11", 53.789, -2.248),
    "Lancaster": ("LA1", 54.047, -2.801),
    "Warrington": ("WA1", 53.390, -2.597),
    "Chester": ("CH1", 53.193, -2.893),
    "Crewe": ("CW1", 53.099, -2.441),
    "Carlisle": ("CA1", 54.892, -2.934),
    # Yorkshire and the Humber
    "Leeds": ("LS1", 53.797, -1.548),
    "Bradford": ("BD1", 53.795, -1.759),
    "Wakefield": ("WF1", 53.683, -1.497),
    "Huddersfield": ("HD1", 53.646, -1.785),
    "Halifax": ("HX1", 53.722, -1.858),
    "Sheffield": ("S1", 53.381, -1.470),
    "Doncaster": ("DN1", 53.523, -1.133),
    "Rotherham": ("S60", 53.430, -1.357),
    "Barnsley": ("S70", 53.553, -1.483),
    "Kingston upon Hull": ("HU1", 53.744, -0.332),
    "York": ("YO1", 53.960, -1.081),
    "Harrogate": ("HG1", 53.992, -1.541),
    "Scarborough": ("YO11", 54.283, -0.400),
    "Grimsby": ("DN31", 53.567, -0.081),
    "Scunthorpe": ("DN15", 53.588, -0.654),
    # East Midlands
    "Nottingham": ("NG1", 52.954, -1.150),
    "Mansfield": ("NG18", 53.144, -1.198),
    "Leicester": ("LE1", 52.637, -1.135),
    "Loughborough": ("LE11", 52.772, -1.206),
    "Derby": ("DE1", 52.922, -1.477),
    "Chesterfield": ("S40", 53.236, -1.428),
    "Northampton": ("NN1", 52.237, -0.897),
    "Lincoln": ("LN1", 53.234, -0.538),
    "Boston": ("PE21", 52.979, -0.027),
    # West Midlands
    "Birmingham": ("B1", 52.480, -1.903),
    "Coventry": ("CV1", 52.408, -1.510),
    "Wolverhampton": ("WV1", 52.586, -2.129),
    "Walsall": ("WS1", 52.586, -1.982),
    "Dudley": ("DY1", 52.512, -2.081),
    "West Bromwich": ("B70", 52.519, -1.995),
    "Solihull": ("B91", 52.412, -1.778),
    "Stoke-on-Trent": ("ST1", 53.003, -2.180),
    "Stafford": ("ST16", 52.806, -2.117),
    "Worcester": ("WR1", 52.192, -2.220),
    "Hereford": ("HR1", 52.056, -2.716),
    "Telford": ("TF3", 52.677, -2.449),
    "Shrewsbury": ("SY1", 52.708, -2.754),
    "Nuneaton": ("CV11", 52.523, -1.468),
    # East of England
    "Norwich": ("NR1", 52.630, 1.297),
    "King's Lynn": ("PE30", 52.754, 0.396),
    "Cambridge": ("CB2", 52.205, 0.119),
    "Peterborough": ("PE1", 52.573, -0.241),
    "Luton": ("LU1", 51.879, -0.418),
    "Bedford": ("MK40", 52.136, -0.467),
    "Ipswich": ("IP1", 52.057, 1.148),
    "Colchester": ("CO1", 51.889, 0.901),
    "Chelmsford": ("CM1", 51.736, 0.469),
    "Southend-on-Sea": ("SS1", 51.538, 0.714),
    "Basildon": ("SS14", 51.576, 0.488),
    "Watford": ("WD17", 51.656, -0.396),
    "Stevenage": ("SG1", 51.903, -0.196),
    # South East
    "Brighton and Hove": ("BN1", 50.822, -0.137),
    "Eastbourne": ("BN21", 50.768, 0.290),
    "Hastings": ("TN34", 50.856, 0.573),
    "Crawley": ("RH10", 51.113, -0.183),
    "Worthing": ("BN11", 50.817, -0.372),
    "Southampton": ("SO14", 50.904, -1.404),
    "Portsmouth": ("PO1", 50.799, -1.091),
    "Basingstoke": ("RG21", 51.263, -1.087),
    "Newport": ("PO30", 50.701, -1.292),
    "Reading": ("RG1", 51.454, -0.973),
    "Slough": ("SL1", 51.511, -0.595),
    "Oxford": ("OX1", 51.752, -1.258),
    "Milton Keynes": ("MK9", 52.040, -0.760),
    "High Wycombe": ("HP11", 51.629, -0.749),
    "Guildford": ("GU1", 51.236, -0.570),
    "Woking": ("GU21", 51.319, -0.558),
    "Maidstone": ("ME14", 51.272, 0.522),
    "Canterbury": ("CT1", 51.280, 1.079),
    "Chatham": ("ME4", 51.380, 0.527),
    "Margate": ("CT9", 51.389, 1.386),
    # South West
    "Bristol": ("BS1", 51.454, -2.588),
    "Bath": ("BA1", 51.381, -2.359),
    "Weston-super-Mare": ("BS23", 51.346, -2.977),
    "Taunton": ("TA1", 51.015, -3.101),
    "Plymouth": ("PL1", 50.371, -4.143),
    "Exeter": ("EX1", 50.722, -3.531),
    "Torquay": ("TQ1", 50.462, -3.525),
    "Truro": ("TR1", 50.263, -5.051),
    "Bournemouth": ("BH1", 50.720, -1.880),
    "Gloucester": ("GL1", 51.864, -2.244),
    "Cheltenham": ("GL50", 51.900, -2.078),
    "Swindon": ("SN1", 51.558, -1.781),
    "Salisbury": ("SP1", 51.069, -1.795),
}


def main(demographics_path, out_path):
    with open(demographics_path, newline="", encoding="utf-8") as f:
        names = [row["NAME"] for row in csv.DictReader(f)]

    missing = [n for n in names if n not in PLACES]
    extra = [n for n in PLACES if n not in names]
    if missing or extra:
        raise SystemExit(f"missing coordinates: {missing}\nnot in demographics: {extra}")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["", "USPS", "ST", "NAME", "ZCTA5", "LAT", "LON"])
        for name in names:
            postcode, lat, lon = PLACES[name]
            w.writerow(["", STATE, ABBR, name, postcode, lat, lon])
    print(f"wrote {len(names)} places")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
