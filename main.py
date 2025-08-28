import asyncio
import pandas as pd
from src.screenshot_shows_state import take_seat_counts_from_csv
from src.coming_soon import search_movie
import itertools
from dotenv import load_dotenv
import os
load_dotenv()




state_to_city_slugs = {
    
    "Alabama": ["birmingham-al"],
    # "Alabama": ["birmingham-al", "mobile-al", "montgomery-al"],
    "Arizona": ["phoenix-az", "tucson-az", "flagstaff-az"],
    "Alaska": ["anchorage-ak", "fairbanks-ak", "juneau-ak"],
    "American Samoa": ["pago-pago-as"],
    "Arkansas": ["little-rock-ar", "fayetteville-ar", "fort-smith-ar"],
    "California": ["los-angeles-ca", "san-francisco-ca", "san-diego-ca", "sacramento-ca"],
    "Colorado": ["denver-co", "colorado-springs-co", "boulder-co"],
    "Connecticut": ["hartford-ct", "new-haven-ct", "stamford-ct"],
    "Delaware": ["wilmington-de", "dover-de"],
    "District of Columbia": ["washington-dc"],
    "Florida": ["miami-fl", "orlando-fl", "tampa-fl", "jacksonville-fl"],
    "Georgia": ["atlanta-ga", "savannah-ga", "augusta-ga"],
    "Guam": ["hagatna-gu"],
    "Hawaii": ["honolulu-hi", "kahului-hi", "lihue-hi"],
    "Idaho": ["boise-id", "idaho-falls-id", "twin-falls-id"],
    "Illinois": ["chicago-il", "springfield-il", "peoria-il"],
    "Indiana": ["indianapolis-in", "fort-wayne-in", "south-bend-in"],
    "Iowa": ["des-moines-ia", "cedar-rapids-ia", "iowa-city-ia"],
    "Kansas": ["wichita-ks", "topeka-ks", "overland-park-ks"],
    "Kentucky": ["louisville-ky", "lexington-ky", "bowling-green-ky"],
    "Louisiana": ["new-orleans-la", "baton-rouge-la", "lafayette-la"],
    "Maine": ["portland-me", "bangor-me", "augusta-me"],
    "Maryland": ["baltimore-md", "rockville-md", "frederick-md"],
    "Massachusetts": ["boston-ma", "worcester-ma", "springfield-ma"],
    "Michigan": ["detroit-mi", "grand-rapids-mi", "ann-arbor-mi"],
    "Minnesota": ["minneapolis-mn", "st-paul-mn", "duluth-mn"],
    "Mississippi": ["jackson-ms", "gulfport-ms", "tupelo-ms"],
    "Missouri": ["kansas-city-mo", "st-louis-mo", "springfield-mo"],
    "Montana": ["billings-mt", "missoula-mt", "bozeman-mt"],
    "Nebraska": ["omaha-ne", "lincoln-ne", "grand-island-ne"],
    "Nevada": ["las-vegas-nv", "reno-nv", "carson-city-nv"],
    "New Hampshire": ["manchester-nh", "nashua-nh", "concord-nh"],
    "New Jersey": ["newark-nj", "jersey-city-nj", "trenton-nj"],
    "New Mexico": ["albuquerque-nm", "santa-fe-nm", "las-cruces-nm"],
    "New York": ["new-york-ny", "buffalo-ny", "rochester-ny", "albany-ny"],
    "North Carolina": ["charlotte-nc", "raleigh-nc", "asheville-nc"],
    "North Dakota": ["fargo-nd", "bismarck-nd", "grand-forks-nd"],
    "Northern Mariana Islands": ["saipan-mp"],
    "Ohio": ["columbus-oh", "cleveland-oh", "cincinnati-oh"],
    "Oklahoma": ["oklahoma-city-ok", "tulsa-ok", "norman-ok"],
    "Oregon": ["portland-or", "eugene-or", "salem-or"],
    "Pennsylvania": ["philadelphia-pa", "pittsburgh-pa", "harrisburg-pa"],
    "Puerto Rico": ["san-juan-pr", "ponce-pr", "mayaguez-pr"],
    "Rhode Island": ["providence-ri", "newport-ri"],
    "South Carolina": ["charleston-sc", "columbia-sc", "greenville-sc"],
    "South Dakota": ["sioux-falls-sd", "rapid-city-sd"],
    "Tennessee": ["nashville-tn", "memphis-tn", "knoxville-tn"],
    "Texas": ["houston-tx", "dallas-tx", "austin-tx", "san-antonio-tx"],
    "Utah": ["salt-lake-city-ut", "provo-ut", "ogden-ut"],
    "Vermont": ["burlington-vt", "montpelier-vt"],
    "Virgin Islands": ["charlotte-amalie-vi"],
    "Virginia": ["virginia-beach-va", "richmond-va", "norfolk-va"],
    "Washington": ["seattle-wa", "spokane-wa", "tacoma-wa"],
    "West Virginia": ["charleston-wv", "morgantown-wv", "huntington-wv"],
    "Wisconsin": ["milwaukee-wi", "madison-wi", "green-bay-wi"],
    "Wyoming": ["cheyenne-wy", "casper-wy", "jackson-wy"]
}



if __name__ == "__main__":
    movie = os.getenv("MOVIE")
    print(f"MOVIE : {movie}")
    # state = os.getenv("STATE")
    all_city_dfs = []
    for key, values in itertools.islice(state_to_city_slugs.items(), 1):
        
        print(key, values)
        for each_city in values:
            print(each_city)
            city_results = asyncio.run(search_movie(movie, each_city))
            city_df = pd.DataFrame(city_results)
            all_city_dfs.append(city_df)
    combined_cities_df = pd.concat(all_city_dfs, ignore_index=True)
    print(f"Columns : {combined_cities_df.columns}")
    combined_cities_df.to_csv(f"outputs/{movie}_shows_df.csv")
    print(combined_cities_df)
    debug = False
    asyncio.run(take_seat_counts_from_csv(INPUT_CSV=f"outputs/{movie}_shows_df.csv",
                                          OUTPUT_CSV=f"outputs/{movie}_seat_count.csv",
                                          debug=False))
    print("completed")

