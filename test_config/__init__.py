

# config parameter specifying supported output formats
class OutputFormat:
    JSON = 'json'
    XML = 'xml'

ALLOWED_OUTPUT_FORMATS = [OutputFormat.JSON, OutputFormat.XML]

# global application configuration parameter
DEFAULT_API_OUTPUT_TYPE = OutputFormat.JSON

# # global variable for default language format
DEFAULT_API_LANGUAGE_FORMAT = 'en-US'

# # global variable for default language format for user and partner
DEFAULT_LANGUAGE_FORMAT_FOR_USER = 'en'

# global limit configuration value for get requests
DEFAULT_LIST_LIMIT = 1000

ERROR_404_HELP = False
