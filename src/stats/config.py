##This is needed because some pitcher stats need inverted percentiles (lower is better)
##All new stats added will need to be added to the stat_config in order to have percentiles calculated.

STAT_CONFIG = {
    "ERA": {"ascending": True},
    "WHIP": {"ascending": True},
    "SO": {"ascending": False},
    "OPS": {"ascending": False},
    "AVG": {"ascending": False},
    "HR": {"ascending": False},
}