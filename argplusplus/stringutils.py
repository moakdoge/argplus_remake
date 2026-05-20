import re
_NORMALIZE_ST = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')

def is_blank(st: str):
    '''Checks if a string is blank'''
    p1 = st.replace(" ", "")
    p2 = p1.strip("\n")
    return p2 == ""

def generate_dashes(st: str):
    '''Converts a string like `example string` or `example_string` to `example-string`'''
    return st.replace(" ", "-").replace("_", "-")

def normalize_name(st: str):
    '''Normallizes a function name to a good command; raises NameError if invalid.'''
    
    #first, let's clean it up
    new = generate_dashes(st)
    
    valid = _NORMALIZE_ST.fullmatch(new)
    if not valid:
        raise NameError(f"Function name of {st} is not valid!")
    
    return new