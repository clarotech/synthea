"""Generate an approximate England demographics CSV in Synthea's demographics.csv format.

Populations: approximate Census 2021 local-authority figures (thousands), labelled by main town.
Ethnicity: approximate Census 2021 shares (White / Asian / Black / Mixed+Other).
Age, income and education: England-level profiles, shifted by a per-place profile tag.
"""
import csv
import sys

STATE = "England"

# Age profiles: 18 five-year bands, 0-4 ... 85+ (percent, normalised below)
AGE = {
    "avg":   [5.4, 5.9, 6.0, 5.6, 6.0, 6.7, 7.0, 6.8, 6.4, 6.4, 6.9, 6.7, 5.8, 5.0, 5.0, 3.6, 2.5, 2.5],
    "young": [6.0, 5.8, 5.6, 5.8, 8.0, 9.5, 9.5, 8.3, 7.0, 6.3, 6.0, 5.3, 4.3, 3.4, 3.0, 2.1, 1.4, 1.3],
    "old":   [4.3, 4.9, 5.3, 5.1, 4.6, 5.0, 5.4, 5.4, 5.3, 5.8, 6.9, 7.6, 7.4, 6.9, 7.3, 5.4, 3.8, 3.6],
}

# Gross household income bands in thousands (read as GBP): 0-10 ... 200+
INCOME = {
    "avg":  [5, 8, 16, 14, 17, 18, 10, 8, 2.5, 1.5],
    "high": [3, 5, 11, 11, 15, 19, 13, 14, 5, 4],
    "low":  [7, 11, 20, 16, 17, 15, 7, 5, 1.2, 0.8],
}

# Highest qualification, age 16+, mapped to Synthea's US categories:
# LESS_THAN_HS = none + Level 1, HS_DEGREE = Level 2 + apprenticeship + other,
# SOME_COLLEGE = Level 3, BS_DEGREE = Level 4+
EDUCATION = {
    "avg":  [27.8, 21.4, 16.9, 33.9],
    "high": [18.0, 17.0, 15.0, 50.0],
    "low":  [34.0, 25.0, 17.0, 24.0],
}

MALE = 0.49

# name, county / authority, population (thousands), white, asian, black, other, age profile, income profile
PLACES = [
    # Greater London
    ("Barking and Dagenham", "Greater London", 219, 45, 25, 21, 9, "young", "low"),
    ("Barnet", "Greater London", 389, 58, 19, 8, 15, "young", "high"),
    ("Bexley", "Greater London", 246, 72, 9, 12, 7, "avg", "avg"),
    ("Brent", "Greater London", 339, 35, 34, 18, 13, "young", "avg"),
    ("Bromley", "Greater London", 330, 77, 7, 8, 8, "avg", "high"),
    ("Camden", "Greater London", 210, 60, 18, 9, 13, "young", "high"),
    ("City of London", "Greater London", 8.6, 69, 19, 3, 9, "young", "high"),
    ("Croydon", "Greater London", 391, 48, 18, 23, 11, "young", "avg"),
    ("Ealing", "Greater London", 367, 43, 31, 11, 15, "young", "avg"),
    ("Enfield", "Greater London", 330, 52, 12, 18, 18, "young", "avg"),
    ("Greenwich", "Greater London", 289, 55, 16, 19, 10, "young", "avg"),
    ("Hackney", "Greater London", 259, 53, 10, 21, 16, "young", "avg"),
    ("Hammersmith and Fulham", "Greater London", 183, 63, 11, 12, 14, "young", "high"),
    ("Haringey", "Greater London", 264, 57, 9, 17, 17, "young", "avg"),
    ("Harrow", "Greater London", 261, 37, 46, 8, 9, "avg", "avg"),
    ("Havering", "Greater London", 262, 75, 10, 9, 6, "avg", "avg"),
    ("Hillingdon", "Greater London", 305, 48, 33, 8, 11, "young", "avg"),
    ("Hounslow", "Greater London", 288, 44, 37, 7, 12, "young", "avg"),
    ("Islington", "Greater London", 217, 62, 10, 13, 15, "young", "high"),
    ("Kensington and Chelsea", "Greater London", 143, 63, 13, 7, 17, "young", "high"),
    ("Kingston upon Thames", "Greater London", 168, 67, 19, 3, 11, "young", "high"),
    ("Lambeth", "Greater London", 317, 55, 7, 24, 14, "young", "avg"),
    ("Lewisham", "Greater London", 300, 52, 9, 27, 12, "young", "avg"),
    ("Merton", "Greater London", 215, 60, 18, 11, 11, "young", "high"),
    ("Newham", "Greater London", 351, 31, 42, 18, 9, "young", "low"),
    ("Redbridge", "Greater London", 311, 35, 47, 9, 9, "young", "avg"),
    ("Richmond upon Thames", "Greater London", 195, 79, 9, 2, 10, "avg", "high"),
    ("Southwark", "Greater London", 307, 51, 10, 25, 14, "young", "avg"),
    ("Sutton", "Greater London", 209, 71, 15, 6, 8, "avg", "high"),
    ("Tower Hamlets", "Greater London", 310, 39, 44, 7, 10, "young", "low"),
    ("Waltham Forest", "Greater London", 278, 53, 22, 14, 11, "young", "avg"),
    ("Wandsworth", "Greater London", 328, 68, 11, 10, 11, "young", "high"),
    ("Westminster", "Greater London", 205, 55, 17, 8, 20, "young", "high"),
    # North East
    ("Newcastle upon Tyne", "Tyne and Wear", 300, 80, 11, 3, 6, "young", "avg"),
    ("Sunderland", "Tyne and Wear", 274, 94, 3, 1, 2, "avg", "low"),
    ("Gateshead", "Tyne and Wear", 196, 93, 3, 1, 3, "avg", "low"),
    ("South Shields", "Tyne and Wear", 148, 94, 3, 0.5, 2.5, "old", "low"),
    ("North Shields", "Tyne and Wear", 209, 94, 3, 1, 2, "old", "avg"),
    ("Middlesbrough", "North Yorkshire", 143, 82, 11, 3, 4, "avg", "low"),
    ("Stockton-on-Tees", "County Durham", 197, 92, 4, 1, 3, "avg", "avg"),
    ("Darlington", "County Durham", 108, 93, 3, 1, 3, "avg", "avg"),
    ("Hartlepool", "County Durham", 92, 95, 2, 1, 2, "avg", "low"),
    ("Durham", "County Durham", 522, 96, 1.5, 0.5, 2, "old", "low"),
    ("Morpeth", "Northumberland", 320, 97, 1, 0.3, 1.7, "old", "avg"),
    # North West
    ("Manchester", "Greater Manchester", 552, 57, 21, 12, 10, "young", "low"),
    ("Salford", "Greater Manchester", 270, 78, 7, 8, 7, "young", "low"),
    ("Bolton", "Greater Manchester", 296, 71, 21, 3, 5, "avg", "low"),
    ("Oldham", "Greater Manchester", 242, 69, 24, 3, 4, "avg", "low"),
    ("Rochdale", "Greater Manchester", 223, 76, 18, 2, 4, "avg", "low"),
    ("Stockport", "Greater Manchester", 295, 88, 6, 1.5, 4.5, "avg", "high"),
    ("Wigan", "Greater Manchester", 330, 94, 2, 1.5, 2.5, "avg", "avg"),
    ("Bury", "Greater Manchester", 193, 82, 12, 1.5, 4.5, "avg", "avg"),
    ("Altrincham", "Greater Manchester", 235, 77, 12, 4, 7, "avg", "high"),
    ("Ashton-under-Lyne", "Greater Manchester", 231, 86, 9, 2, 3, "avg", "low"),
    ("Liverpool", "Merseyside", 486, 84, 5, 4, 7, "young", "low"),
    ("Birkenhead", "Merseyside", 320, 95, 2, 0.5, 2.5, "old", "avg"),
    ("St Helens", "Merseyside", 183, 96, 1.5, 0.5, 2, "avg", "low"),
    ("Southport", "Merseyside", 280, 95, 1.5, 0.5, 3, "old", "avg"),
    ("Preston", "Lancashire", 147, 73, 19, 2, 6, "young", "avg"),
    ("Blackburn", "Lancashire", 154, 59, 35, 1, 5, "avg", "low"),
    ("Blackpool", "Lancashire", 141, 94, 2, 1, 3, "old", "low"),
    ("Burnley", "Lancashire", 95, 81, 16, 0.5, 2.5, "avg", "low"),
    ("Lancaster", "Lancashire", 142, 92, 4, 1, 3, "avg", "avg"),
    ("Warrington", "Cheshire", 211, 92, 4, 1, 3, "avg", "high"),
    ("Chester", "Cheshire", 357, 95, 2, 0.5, 2.5, "old", "high"),
    ("Crewe", "Cheshire", 399, 95, 2, 0.5, 2.5, "old", "high"),
    ("Carlisle", "Cumbria", 109, 96, 1.5, 0.5, 2, "old", "avg"),
    # Yorkshire and the Humber
    ("Leeds", "West Yorkshire", 812, 79, 10, 5, 6, "young", "avg"),
    ("Bradford", "West Yorkshire", 546, 61, 32, 2, 5, "avg", "low"),
    ("Wakefield", "West Yorkshire", 353, 93, 3, 1, 3, "avg", "avg"),
    ("Huddersfield", "West Yorkshire", 434, 74, 21, 2, 3, "avg", "avg"),
    ("Halifax", "West Yorkshire", 207, 86, 11, 0.5, 2.5, "avg", "avg"),
    ("Sheffield", "South Yorkshire", 556, 79, 10, 5, 6, "young", "avg"),
    ("Doncaster", "South Yorkshire", 308, 92, 3, 1.5, 3.5, "avg", "low"),
    ("Rotherham", "South Yorkshire", 265, 89, 6, 1.5, 3.5, "avg", "low"),
    ("Barnsley", "South Yorkshire", 245, 96, 1.5, 0.5, 2, "avg", "low"),
    ("Kingston upon Hull", "East Riding of Yorkshire", 267, 89, 3, 3, 5, "avg", "low"),
    ("York", "North Yorkshire", 203, 91, 4, 1, 4, "young", "high"),
    ("Harrogate", "North Yorkshire", 162, 96, 2, 0.3, 1.7, "old", "high"),
    ("Scarborough", "North Yorkshire", 108, 97, 1, 0.3, 1.7, "old", "low"),
    ("Grimsby", "Lincolnshire", 157, 95, 2, 0.5, 2.5, "avg", "low"),
    ("Scunthorpe", "Lincolnshire", 169, 94, 3, 0.5, 2.5, "avg", "avg"),
    # East Midlands
    ("Nottingham", "Nottinghamshire", 324, 66, 15, 10, 9, "young", "low"),
    ("Mansfield", "Nottinghamshire", 111, 95, 1.5, 1, 2.5, "avg", "low"),
    ("Leicester", "Leicestershire", 368, 41, 43, 8, 8, "young", "low"),
    ("Loughborough", "Leicestershire", 183, 83, 12, 1.5, 3.5, "young", "avg"),
    ("Derby", "Derbyshire", 261, 74, 16, 4, 6, "avg", "avg"),
    ("Chesterfield", "Derbyshire", 104, 96, 1.5, 0.5, 2, "old", "avg"),
    ("Northampton", "Northamptonshire", 425, 86, 6, 4, 4, "avg", "avg"),
    ("Lincoln", "Lincolnshire", 103, 90, 4, 1.5, 4.5, "young", "avg"),
    ("Boston", "Lincolnshire", 70, 95, 1.5, 0.5, 3, "old", "low"),
    # West Midlands
    ("Birmingham", "West Midlands", 1145, 49, 31, 11, 9, "young", "low"),
    ("Coventry", "West Midlands", 345, 66, 19, 9, 6, "young", "avg"),
    ("Wolverhampton", "West Midlands", 264, 59, 24, 9, 8, "avg", "low"),
    ("Walsall", "West Midlands", 284, 70, 20, 4, 6, "avg", "low"),
    ("Dudley", "West Midlands", 323, 84, 10, 2, 4, "avg", "avg"),
    ("West Bromwich", "West Midlands", 341, 54, 29, 10, 7, "avg", "low"),
    ("Solihull", "West Midlands", 216, 84, 10, 2, 4, "avg", "high"),
    ("Stoke-on-Trent", "Staffordshire", 258, 83, 10, 3, 4, "avg", "low"),
    ("Stafford", "Staffordshire", 137, 94, 3, 0.7, 2.3, "old", "avg"),
    ("Worcester", "Worcestershire", 103, 90, 5, 1.5, 3.5, "avg", "avg"),
    ("Hereford", "Herefordshire", 187, 97, 1, 0.3, 1.7, "old", "avg"),
    ("Telford", "Shropshire", 186, 89, 6, 2, 3, "avg", "avg"),
    ("Shrewsbury", "Shropshire", 323, 97, 1, 0.3, 1.7, "old", "avg"),
    ("Nuneaton", "Warwickshire", 134, 90, 6, 1.5, 2.5, "avg", "avg"),
    # East of England
    ("Norwich", "Norfolk", 144, 89, 5, 2, 4, "young", "avg"),
    ("King's Lynn", "Norfolk", 155, 96, 1.5, 0.5, 2, "old", "avg"),
    ("Cambridge", "Cambridgeshire", 146, 75, 14, 2, 9, "young", "high"),
    ("Peterborough", "Cambridgeshire", 216, 74, 15, 4, 7, "avg", "avg"),
    ("Luton", "Bedfordshire", 225, 37, 39, 13, 11, "young", "low"),
    ("Bedford", "Bedfordshire", 185, 70, 18, 6, 6, "avg", "avg"),
    ("Ipswich", "Suffolk", 140, 84, 6, 4, 6, "avg", "avg"),
    ("Colchester", "Essex", 192, 87, 6, 3, 4, "avg", "avg"),
    ("Chelmsford", "Essex", 181, 89, 5, 2.5, 3.5, "avg", "high"),
    ("Southend-on-Sea", "Essex", 181, 85, 6, 4, 5, "old", "avg"),
    ("Basildon", "Essex", 188, 84, 5, 7, 4, "avg", "avg"),
    ("Watford", "Hertfordshire", 102, 62, 25, 6, 7, "young", "high"),
    ("Stevenage", "Hertfordshire", 89, 81, 7, 7, 5, "avg", "avg"),
    # South East
    ("Brighton and Hove", "East Sussex", 277, 85, 6, 2, 7, "young", "avg"),
    ("Eastbourne", "East Sussex", 101, 91, 3, 1.5, 4.5, "old", "avg"),
    ("Hastings", "East Sussex", 91, 91, 2.5, 2, 4.5, "old", "low"),
    ("Crawley", "West Sussex", 118, 64, 24, 6, 6, "avg", "avg"),
    ("Worthing", "West Sussex", 111, 90, 4, 1.5, 4.5, "old", "avg"),
    ("Southampton", "Hampshire", 249, 78, 12, 4, 6, "young", "avg"),
    ("Portsmouth", "Hampshire", 208, 84, 9, 3, 4, "young", "avg"),
    ("Basingstoke", "Hampshire", 185, 87, 6, 3, 4, "avg", "high"),
    ("Newport", "Isle of Wight", 140, 97, 1, 0.3, 1.7, "old", "low"),
    ("Reading", "Berkshire", 174, 61, 20, 9, 10, "young", "high"),
    ("Slough", "Berkshire", 158, 28, 47, 9, 16, "young", "avg"),
    ("Oxford", "Oxfordshire", 162, 71, 16, 4, 9, "young", "high"),
    ("Milton Keynes", "Buckinghamshire", 287, 69, 14, 11, 6, "avg", "high"),
    ("High Wycombe", "Buckinghamshire", 553, 80, 13, 2.5, 4.5, "avg", "high"),
    ("Guildford", "Surrey", 143, 84, 9, 2, 5, "young", "high"),
    ("Woking", "Surrey", 103, 79, 14, 2, 5, "avg", "high"),
    ("Maidstone", "Kent", 175, 88, 5, 3, 4, "avg", "avg"),
    ("Canterbury", "Kent", 157, 90, 4, 2, 4, "young", "avg"),
    ("Chatham", "Kent", 279, 83, 6, 6, 5, "avg", "avg"),
    ("Margate", "Kent", 141, 92, 2.5, 1.5, 4, "old", "low"),
    # South West
    ("Bristol", "Bristol", 472, 77, 7, 6, 10, "young", "avg"),
    ("Bath", "Somerset", 194, 91, 4, 1, 4, "avg", "high"),
    ("Weston-super-Mare", "Somerset", 216, 95, 2, 0.5, 2.5, "old", "avg"),
    ("Taunton", "Somerset", 160, 96, 1.5, 0.5, 2, "old", "avg"),
    ("Plymouth", "Devon", 264, 93, 3, 1, 3, "avg", "low"),
    ("Exeter", "Devon", 131, 89, 5, 1.5, 4.5, "young", "avg"),
    ("Torquay", "Devon", 139, 96, 1.5, 0.3, 2.2, "old", "low"),
    ("Truro", "Cornwall", 570, 97, 1, 0.3, 1.7, "old", "low"),
    ("Bournemouth", "Dorset", 401, 89, 4, 1.5, 5.5, "old", "avg"),
    ("Gloucester", "Gloucestershire", 132, 85, 7, 3, 5, "avg", "avg"),
    ("Cheltenham", "Gloucestershire", 119, 89, 5, 1.5, 4.5, "avg", "high"),
    ("Swindon", "Wiltshire", 233, 84, 9, 3, 4, "avg", "avg"),
    ("Salisbury", "Wiltshire", 510, 95, 2, 0.7, 2.3, "old", "high"),
]

AGE_COLS = [str(i) for i in range(1, 19)]
INCOME_COLS = ["00..10", "10..15", "15..25", "25..35", "35..50",
               "50..75", "75..100", "100..150", "150..200", "200..999"]
EDU_COLS = ["LESS_THAN_HS", "HS_DEGREE", "SOME_COLLEGE", "BS_DEGREE"]
HEADER = (["ID", "COUNTY", "NAME", "STNAME", "POPESTIMATE2015", "CTYNAME", "TOT_POP",
           "TOT_MALE", "TOT_FEMALE", "WHITE", "HISPANIC", "BLACK", "ASIAN", "NATIVE", "OTHER"]
          + AGE_COLS + INCOME_COLS + EDU_COLS)


def norm(values):
    total = float(sum(values))
    out = [round(v / total, 6) for v in values]
    # push rounding drift into the largest bucket so each distribution sums to exactly 1
    out[out.index(max(out))] += round(1.0 - sum(out), 6)
    return [round(v, 6) for v in out]


def main(path):
    names = [p[0] for p in PLACES]
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        raise SystemExit(f"duplicate place names: {dupes}")

    counties = {}
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(HEADER)
        for i, (name, county, pop_k, wh, asn, blk, oth, age, inc) in enumerate(PLACES, start=1):
            county_code = counties.setdefault(county, f"{len(counties) + 1:03d}")
            pop = int(round(pop_k * 1000))
            white, asian, black, other = norm([wh, asn, blk, oth])
            row = [f"UK{i:04d}", county_code, name, STATE, pop, county, pop,
                   MALE, round(1 - MALE, 2),
                   white, 0.0, black, asian, 0.0, other]
            row += norm(AGE[age]) + norm(INCOME[inc]) + norm(EDUCATION[inc])
            w.writerow(row)
    total = sum(p[2] for p in PLACES)
    print(f"wrote {len(PLACES)} places, total population {total * 1000:,.0f}")


if __name__ == "__main__":
    main(sys.argv[1])
