from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Airport:
    iata: str
    name: str
    city: str
    country: str

    def display(self) -> str:
        return f"{self.iata} — {self.city} ({self.name})"


MAJOR_AIRPORTS: dict[str, Airport] = {
    # North America
    "ATL": Airport("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta", "US"),
    "LAX": Airport("LAX", "Los Angeles International", "Los Angeles", "US"),
    "ORD": Airport("ORD", "O'Hare International", "Chicago", "US"),
    "DFW": Airport("DFW", "Dallas/Fort Worth International", "Dallas", "US"),
    "DEN": Airport("DEN", "Denver International", "Denver", "US"),
    "JFK": Airport("JFK", "John F. Kennedy International", "New York", "US"),
    "SFO": Airport("SFO", "San Francisco International", "San Francisco", "US"),
    "LAS": Airport("LAS", "Harry Reid International", "Las Vegas", "US"),
    "MCO": Airport("MCO", "Orlando International", "Orlando", "US"),
    "SEA": Airport("SEA", "Seattle-Tacoma International", "Seattle", "US"),
    "MIA": Airport("MIA", "Miami International", "Miami", "US"),
    "PHX": Airport("PHX", "Phoenix Sky Harbor International", "Phoenix", "US"),
    "EWR": Airport("EWR", "Newark Liberty International", "Newark", "US"),
    "MSP": Airport("MSP", "Minneapolis-Saint Paul International", "Minneapolis", "US"),
    "BOS": Airport("BOS", "Boston Logan International", "Boston", "US"),
    "DTW": Airport("DTW", "Detroit Metropolitan Wayne County", "Detroit", "US"),
    "PHL": Airport("PHL", "Philadelphia International", "Philadelphia", "US"),
    "LGA": Airport("LGA", "LaGuardia", "New York", "US"),
    "FLL": Airport("FLL", "Fort Lauderdale-Hollywood International", "Fort Lauderdale", "US"),
    "BWI": Airport("BWI", "Baltimore/Washington International", "Baltimore", "US"),
    "IAD": Airport("IAD", "Washington Dulles International", "Washington", "US"),
    "DCA": Airport("DCA", "Ronald Reagan Washington National", "Washington", "US"),
    "MDW": Airport("MDW", "Chicago Midway International", "Chicago", "US"),
    "SLC": Airport("SLC", "Salt Lake City International", "Salt Lake City", "US"),
    "PDX": Airport("PDX", "Portland International", "Portland", "US"),
    "HNL": Airport("HNL", "Daniel K. Inouye International", "Honolulu", "US"),
    "SAN": Airport("SAN", "San Diego International", "San Diego", "US"),
    "TPA": Airport("TPA", "Tampa International", "Tampa", "US"),
    "AUS": Airport("AUS", "Austin-Bergstrom International", "Austin", "US"),
    "IAH": Airport("IAH", "George Bush Intercontinental", "Houston", "US"),
    "HOU": Airport("HOU", "Houston William P. Hobby", "Houston", "US"),
    "BNA": Airport("BNA", "Nashville International", "Nashville", "US"),
    "RDU": Airport("RDU", "Raleigh-Durham International", "Raleigh", "US"),
    "STL": Airport("STL", "St. Louis Lambert International", "St. Louis", "US"),
    "CLE": Airport("CLE", "Cleveland Hopkins International", "Cleveland", "US"),
    "MCI": Airport("MCI", "Kansas City International", "Kansas City", "US"),
    "OAK": Airport("OAK", "Oakland International", "Oakland", "US"),
    "SJC": Airport("SJC", "San José International", "San Jose", "US"),
    "BUR": Airport("BUR", "Hollywood Burbank Airport", "Burbank", "US"),
    "YYZ": Airport("YYZ", "Toronto Pearson International", "Toronto", "CA"),
    "YVR": Airport("YVR", "Vancouver International", "Vancouver", "CA"),
    "YUL": Airport("YUL", "Montréal-Trudeau International", "Montreal", "CA"),
    "YYC": Airport("YYC", "Calgary International", "Calgary", "CA"),
    "YEG": Airport("YEG", "Edmonton International", "Edmonton", "CA"),
    "MEX": Airport("MEX", "Mexico City International", "Mexico City", "MX"),
    "CUN": Airport("CUN", "Cancún International", "Cancún", "MX"),
    "GRU": Airport("GRU", "São Paulo/Guarulhos International", "São Paulo", "BR"),
    "GIG": Airport("GIG", "Rio de Janeiro/Galeão International", "Rio de Janeiro", "BR"),
    "BOG": Airport("BOG", "El Dorado International", "Bogotá", "CO"),
    "LIM": Airport("LIM", "Jorge Chávez International", "Lima", "PE"),
    "EZE": Airport("EZE", "Ministro Pistarini International", "Buenos Aires", "AR"),
    "SCL": Airport("SCL", "Arturo Merino Benítez International", "Santiago", "CL"),
    "UIO": Airport("UIO", "Mariscal Sucre International", "Quito", "EC"),
    # Europe
    "LHR": Airport("LHR", "London Heathrow", "London", "GB"),
    "LGW": Airport("LGW", "London Gatwick", "London", "GB"),
    "STN": Airport("STN", "London Stansted", "London", "GB"),
    "CDG": Airport("CDG", "Paris Charles de Gaulle", "Paris", "FR"),
    "ORY": Airport("ORY", "Paris Orly", "Paris", "FR"),
    "AMS": Airport("AMS", "Amsterdam Schiphol", "Amsterdam", "NL"),
    "FRA": Airport("FRA", "Frankfurt Airport", "Frankfurt", "DE"),
    "MUC": Airport("MUC", "Munich Airport", "Munich", "DE"),
    "TXL": Airport("TXL", "Berlin Brandenburg Airport", "Berlin", "DE"),
    "BER": Airport("BER", "Berlin Brandenburg Airport", "Berlin", "DE"),
    "MAD": Airport("MAD", "Adolfo Suárez Madrid-Barajas", "Madrid", "ES"),
    "BCN": Airport("BCN", "Barcelona El Prat", "Barcelona", "ES"),
    "FCO": Airport("FCO", "Leonardo da Vinci International", "Rome", "IT"),
    "MXP": Airport("MXP", "Milan Malpensa International", "Milan", "IT"),
    "VCE": Airport("VCE", "Venice Marco Polo Airport", "Venice", "IT"),
    "ZRH": Airport("ZRH", "Zurich Airport", "Zurich", "CH"),
    "GVA": Airport("GVA", "Geneva Airport", "Geneva", "CH"),
    "VIE": Airport("VIE", "Vienna International Airport", "Vienna", "AT"),
    "CPH": Airport("CPH", "Copenhagen Airport", "Copenhagen", "DK"),
    "OSL": Airport("OSL", "Oslo Gardermoen Airport", "Oslo", "NO"),
    "ARN": Airport("ARN", "Stockholm Arlanda Airport", "Stockholm", "SE"),
    "HEL": Airport("HEL", "Helsinki-Vantaa Airport", "Helsinki", "FI"),
    "LIS": Airport("LIS", "Humberto Delgado Airport", "Lisbon", "PT"),
    "OPO": Airport("OPO", "Francisco Sá Carneiro Airport", "Porto", "PT"),
    "ATH": Airport("ATH", "Athens International Airport", "Athens", "GR"),
    "IST": Airport("IST", "Istanbul Airport", "Istanbul", "TR"),
    "SAW": Airport("SAW", "Istanbul Sabiha Gökçen", "Istanbul", "TR"),
    "WAW": Airport("WAW", "Warsaw Chopin Airport", "Warsaw", "PL"),
    "BRU": Airport("BRU", "Brussels Airport", "Brussels", "BE"),
    "DUB": Airport("DUB", "Dublin Airport", "Dublin", "IE"),
    "PRG": Airport("PRG", "Václav Havel Airport Prague", "Prague", "CZ"),
    "BUD": Airport("BUD", "Budapest Ferenc Liszt International", "Budapest", "HU"),
    "KBP": Airport("KBP", "Boryspil International Airport", "Kyiv", "UA"),
    # Middle East & Africa
    "DXB": Airport("DXB", "Dubai International Airport", "Dubai", "AE"),
    "AUH": Airport("AUH", "Abu Dhabi International Airport", "Abu Dhabi", "AE"),
    "DOH": Airport("DOH", "Hamad International Airport", "Doha", "QA"),
    "KWI": Airport("KWI", "Kuwait International Airport", "Kuwait City", "KW"),
    "BAH": Airport("BAH", "Bahrain International Airport", "Manama", "BH"),
    "RUH": Airport("RUH", "King Khalid International Airport", "Riyadh", "SA"),
    "JED": Airport("JED", "King Abdulaziz International Airport", "Jeddah", "SA"),
    "AMM": Airport("AMM", "Queen Alia International Airport", "Amman", "JO"),
    "BEY": Airport("BEY", "Beirut Rafic Hariri International", "Beirut", "LB"),
    "TLV": Airport("TLV", "Ben Gurion Airport", "Tel Aviv", "IL"),
    "CAI": Airport("CAI", "Cairo International Airport", "Cairo", "EG"),
    "JNB": Airport("JNB", "O.R. Tambo International Airport", "Johannesburg", "ZA"),
    "CPT": Airport("CPT", "Cape Town International Airport", "Cape Town", "ZA"),
    "NBO": Airport("NBO", "Jomo Kenyatta International Airport", "Nairobi", "KE"),
    "ADD": Airport("ADD", "Addis Ababa Bole International Airport", "Addis Ababa", "ET"),
    "LOS": Airport("LOS", "Murtala Muhammed International Airport", "Lagos", "NG"),
    "ACC": Airport("ACC", "Kotoka International Airport", "Accra", "GH"),
    "CMN": Airport("CMN", "Mohammed V International Airport", "Casablanca", "MA"),
    # Asia Pacific
    "PEK": Airport("PEK", "Beijing Capital International Airport", "Beijing", "CN"),
    "PKX": Airport("PKX", "Beijing Daxing International Airport", "Beijing", "CN"),
    "PVG": Airport("PVG", "Shanghai Pudong International Airport", "Shanghai", "CN"),
    "SHA": Airport("SHA", "Shanghai Hongqiao International Airport", "Shanghai", "CN"),
    "CAN": Airport("CAN", "Guangzhou Baiyun International Airport", "Guangzhou", "CN"),
    "CTU": Airport("CTU", "Chengdu Tianfu International Airport", "Chengdu", "CN"),
    "HKG": Airport("HKG", "Hong Kong International Airport", "Hong Kong", "HK"),
    "TPE": Airport("TPE", "Taiwan Taoyuan International Airport", "Taipei", "TW"),
    "SIN": Airport("SIN", "Singapore Changi Airport", "Singapore", "SG"),
    "BKK": Airport("BKK", "Suvarnabhumi Airport", "Bangkok", "TH"),
    "DMK": Airport("DMK", "Don Mueang International Airport", "Bangkok", "TH"),
    "KUL": Airport("KUL", "Kuala Lumpur International Airport", "Kuala Lumpur", "MY"),
    "CGK": Airport("CGK", "Soekarno-Hatta International Airport", "Jakarta", "ID"),
    "DPS": Airport("DPS", "Ngurah Rai International Airport", "Bali", "ID"),
    "MNL": Airport("MNL", "Ninoy Aquino International Airport", "Manila", "PH"),
    "SGN": Airport("SGN", "Tan Son Nhat International Airport", "Ho Chi Minh City", "VN"),
    "HAN": Airport("HAN", "Noi Bai International Airport", "Hanoi", "VN"),
    "RGN": Airport("RGN", "Yangon International Airport", "Yangon", "MM"),
    "PNH": Airport("PNH", "Phnom Penh International Airport", "Phnom Penh", "KH"),
    "ICN": Airport("ICN", "Incheon International Airport", "Seoul", "KR"),
    "GMP": Airport("GMP", "Gimpo International Airport", "Seoul", "KR"),
    "NRT": Airport("NRT", "Tokyo Narita International Airport", "Tokyo", "JP"),
    "HND": Airport("HND", "Tokyo Haneda International Airport", "Tokyo", "JP"),
    "KIX": Airport("KIX", "Kansai International Airport", "Osaka", "JP"),
    "CTS": Airport("CTS", "New Chitose Airport", "Sapporo", "JP"),
    "SYD": Airport("SYD", "Sydney Kingsford Smith Airport", "Sydney", "AU"),
    "MEL": Airport("MEL", "Melbourne Airport", "Melbourne", "AU"),
    "BNE": Airport("BNE", "Brisbane Airport", "Brisbane", "AU"),
    "PER": Airport("PER", "Perth Airport", "Perth", "AU"),
    "AKL": Airport("AKL", "Auckland Airport", "Auckland", "NZ"),
    "CHC": Airport("CHC", "Christchurch International Airport", "Christchurch", "NZ"),
    "DEL": Airport("DEL", "Indira Gandhi International Airport", "New Delhi", "IN"),
    "BOM": Airport("BOM", "Chhatrapati Shivaji Maharaj International", "Mumbai", "IN"),
    "BLR": Airport("BLR", "Kempegowda International Airport", "Bengaluru", "IN"),
    "HYD": Airport("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "IN"),
    "MAA": Airport("MAA", "Chennai International Airport", "Chennai", "IN"),
    "CCU": Airport("CCU", "Netaji Subhas Chandra Bose International", "Kolkata", "IN"),
    "KHI": Airport("KHI", "Jinnah International Airport", "Karachi", "PK"),
    "LHE": Airport("LHE", "Allama Iqbal International Airport", "Lahore", "PK"),
    "ISB": Airport("ISB", "Islamabad International Airport", "Islamabad", "PK"),
    "CMB": Airport("CMB", "Bandaranaike International Airport", "Colombo", "LK"),
    "DAC": Airport("DAC", "Hazrat Shahjalal International Airport", "Dhaka", "BD"),
    "KTM": Airport("KTM", "Tribhuvan International Airport", "Kathmandu", "NP"),
    "DME": Airport("DME", "Moscow Domodedovo Airport", "Moscow", "RU"),
    "SVO": Airport("SVO", "Sheremetyevo International Airport", "Moscow", "RU"),
    "LED": Airport("LED", "Pulkovo Airport", "Saint Petersburg", "RU"),
}


# ── Region definitions ────────────────────────────────────────────────────────

# Maps canonical region key (UPPERCASE) → frozenset of ISO country codes
REGIONS: dict[str, frozenset[str]] = {
    "EUROPE": frozenset({
        "GB", "FR", "DE", "ES", "IT", "NL", "CH", "AT", "DK", "NO", "SE",
        "FI", "PT", "GR", "TR", "PL", "BE", "IE", "CZ", "HU", "UA",
    }),
    "NORTH AMERICA": frozenset({"US", "CA", "MX"}),
    "UNITED STATES": frozenset({"US"}),
    "CANADA": frozenset({"CA"}),
    "SOUTH AMERICA": frozenset({"BR", "CO", "PE", "AR", "CL", "EC"}),
    "AMERICAS": frozenset({"US", "CA", "MX", "BR", "CO", "PE", "AR", "CL", "EC"}),
    "ASIA": frozenset({
        "CN", "HK", "TW", "SG", "TH", "MY", "ID", "PH", "VN", "MM",
        "KH", "KR", "JP", "IN", "PK", "LK", "BD", "NP",
    }),
    "ASIA PACIFIC": frozenset({
        "CN", "HK", "TW", "SG", "TH", "MY", "ID", "PH", "VN", "MM",
        "KH", "KR", "JP", "AU", "NZ", "IN", "PK", "LK", "BD", "NP",
    }),
    "SOUTHEAST ASIA": frozenset({"SG", "TH", "MY", "ID", "PH", "VN", "MM", "KH"}),
    "EAST ASIA": frozenset({"CN", "HK", "TW", "KR", "JP"}),
    "SOUTH ASIA": frozenset({"IN", "PK", "LK", "BD", "NP"}),
    "MIDDLE EAST": frozenset({"AE", "QA", "KW", "BH", "SA", "JO", "LB", "IL", "EG"}),
    "AFRICA": frozenset({"ZA", "KE", "ET", "NG", "GH", "MA"}),
    "OCEANIA": frozenset({"AU", "NZ"}),
}


def get_region_airports(region_key: str) -> list[str]:
    """Return IATA codes for all major airports in the given region."""
    countries = REGIONS.get(region_key.upper(), frozenset())
    return [iata for iata, a in MAJOR_AIRPORTS.items() if a.country in countries]


def fuzzy_search_region(query: str) -> list[tuple[str, str]]:
    """Return (canonical_key, display_label) pairs matching query.

    canonical_key is UPPERCASE (e.g. 'EUROPE').
    display_label is title-cased with airport count (e.g. 'Europe  (28 airports)').
    """
    q = query.strip().lower()
    if not q:
        return []
    results = []
    for key in REGIONS:
        if key.lower().startswith(q) or q in key.lower():
            count = len(get_region_airports(key))
            results.append((key, f"{key.title()}  ({count} airports)"))
    return results


def get_airport(iata: str) -> Airport | None:
    """Return Airport for a given IATA code (case-insensitive)."""
    return MAJOR_AIRPORTS.get(iata.upper())


def fuzzy_search_airport(query: str, limit: int = 5) -> list[Airport]:
    """
    Search airports by IATA code, city, or name.
    Returns up to `limit` matches sorted by relevance.
    """
    q = query.strip().lower()
    if not q:
        return []

    exact_iata = MAJOR_AIRPORTS.get(q.upper())
    if exact_iata:
        return [exact_iata]

    results: list[tuple[int, Airport]] = []
    for airport in MAJOR_AIRPORTS.values():
        score = 0
        if airport.iata.lower().startswith(q):
            score += 100
        if airport.city.lower().startswith(q):
            score += 80
        if q in airport.city.lower():
            score += 40
        if q in airport.name.lower():
            score += 20
        if q in airport.country.lower():
            score += 10
        if score > 0:
            results.append((score, airport))

    results.sort(key=lambda x: -x[0])
    return [a for _, a in results[:limit]]
