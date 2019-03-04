# This setting defines whether validator should raise error on Items/Stats that
# don't have a defined Spec
SKIP_ITEMS_WITHOUT_SPEC = False
SKIP_STATS_WITHOUT_SPEC = False

# Whether item fields with empty values should be treated as missing
# missing values do not go through pipeline and are not counted towards coverage
# empty value is bool(value) == False,
# non-iterable values cannot be empty (e.g. bool, integers, floats etc.)
EMPTY_IS_MISSING = True
