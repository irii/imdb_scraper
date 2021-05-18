import re

LIST_ID_PARSER = re.compile(r".*list/(?P<Id>[A-Z0-9]*).*", re.IGNORECASE)
ACTOR_AWARD_ID_PARSER = re.compile(    r".*name/(?P<Id>[A-Z0-9]*)/awards.*", re.IGNORECASE)
ACTOR_ID_PARSER = re.compile(r".*name/(?P<Id>nm[A-Z0-9]*).*", re.IGNORECASE)
MOVIE_CAST_ID_PARSER = re.compile(    r".*title/(?P<Id>tt[A-Z0-9]*)/fullcredits.*", re.IGNORECASE)
MOVIE_ID_PARSER = re.compile(r".*title/(?P<Id>tt[A-Z0-9]*).*", re.IGNORECASE)
ACTOR_FIND_BIRTH_LOCATION_PARSER = re.compile(    r'.*\/search\/name\?birth\_place\=.*')

FILMOSEARCH_ID_PARSER = re.compile(r".*filmosearch[\/]{0,1}\?.*role\=(?P<Id>nm[a-z0-9]*).*", re.IGNORECASE)
FILMOSEARCH_EXTRACT_ACTORID_PARSER = re.compile(r".*role\=(?P<Id>nm[a-z0-9]*).*", re.IGNORECASE)

# Try to get the original image
LINK_EXTRACTOR = re.compile(r"^(?P<Link>.*\@\@).*\.(?P<Extension>[a-z0-9]*)$", re.IGNORECASE)

# Extract extension type
EXTENSION_EXTRACTOR = re.compile(r"[.]*\.(?P<Extension>[a-z0-9]*)$", re.IGNORECASE)

# Converts the given link into a full size image link
def prepareImageLink(link):
    match = LINK_EXTRACTOR.match(link)
    if match:
        return (match.group("Link") + "." + match.group("Extension"), match.group("Extension"))

    match = EXTENSION_EXTRACTOR.match(link)
    if match:
        return (link, match.group("Extension"))

    return None # Not supported link type
