def construct_init_script(custom_init_script: bool = False, level: str = 'easy', db_variant: str = 'flights', type: str = None) -> str:
    init_script = """from dataclasses import dataclass
from typing import Literal

@dataclass
class TaskAnswer:
    answer: str
"""
    if custom_init_script:
        if level == 'hard' and db_variant == 'coffee':
            if type in ["average coffee price", "coffee price change", "coffee price range"]:
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        price: str # The answer format must be a string representing a floating-point number with one decimal place.
    """
            elif type in ['percentage change', 'percentage increase', 'average percentage change']:  
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        percentage: str # The answer format must be a string representing a floating-point number with one decimal place, followed by a percentage sign.
    """        
            elif type == 'average daily volume':
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        volume: str # The answer format must be a string representing a floating-point number with one decimal place.
    """        
            elif type in ["day with the greatest price change", "day with the highest increase"]:
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        date: str # The answer format must be a string representing a date in the format 'YYYY-MM-DD'.
    """
        elif level == 'hard' and db_variant == 'airbnb':
            if type in ['total price', 'average price']:
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        price: str # The answer format must be a string representing a floating-point number with one decimal place, prefixed with a dollar sign.
    """
            elif type == 'cost per night': 
                init_script = """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        cost: str # The answer format must be a string representing an integer, prefixed with a dollar sign.
    """
            elif type == 'average review rates':   
                init_script =  """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        review_rates: str # The answer format must be a string representing a floating-point number with two decimal place.
    """
            elif type == 'proporion of airbnbs':
                init_script =  """from dataclasses import dataclass
    from typing import Literal

    @dataclass
    class TaskAnswer:
        proporion: str # The answer format must be a string representing a floating-point number with one decimal place.
    """                          
    return init_script
        