"""No prebuilt special analyses are enabled; use reviewed Graph/SQL discovery."""
def discover_special_tools():
    return {}

def get_special_tool_endpoints():
    return []

def get_lightweight_references():
    return []

def get_detailed_references():
    return {}

def get_special_tool(tool_name):
    return None

def execute_special_tool(tool_name, **kwargs):
    raise ValueError('This specialized analysis is not supported in Netra')
