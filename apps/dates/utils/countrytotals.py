
class UnrecognizedCountryError(ValueError):
    pass

TOTALS = {
  'US': 21,
  # Jill?!?!?!
}

def get_country_total(country):
    if country in TOTALS:
        return TOTALS[country]
    raise UnrecognizedCountryError(country)
