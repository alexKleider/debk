# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

MAXIMUM_VERBOSITY = 3
EPSILON = 0.01  # We want acuracy to the nearest $0.01.
INDENTATION_MULTIPLIER = 3  

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     #Must jive with 'split' values in CofAs.
DEFAULT_DIR = './debk.d'
# Each entity will have its home directory in DEFAULT_DIR.

# The following files are expected to be in the DEFAULT_DIR directory:
DEFAULT_CofA = "defaultChartOfAccounts"     # A file name.
# The default chart of accounts. (For now: place holders only.)
# A file of this name is kept in DEFAULT_DIR to serve as a template
# during entity creation although a different file can be used, see
# docstring for create_entity().
DEFAULT_Metadata = "defaultMetadata.json"   # A file name.
# A template used during entity creation.
DEFAULT_Entity = "defaultEntity"            # A file name.
# DEFAULT_Entity  - Keeps track of the last entity accessed.
# Its content serves as a default if an entity is required but
# not specified on the command line.

CofA_name = 'CofA'               #| These three files will appear
Journal_name = 'Journal.json'    #| in the home directory of
Metadata_name = 'Metadata.json'  #| each newly created entity.
