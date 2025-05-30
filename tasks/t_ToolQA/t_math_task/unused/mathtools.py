'''
input: formula strings
output: the answer of the mathematical formula
'''

# %%
# import os
# import re
# from operator import pow, truediv, mul, add, sub
# # import wolframalpha

# def calculator(query: str):
#     operators = {
#         '+': add,
#         '-': sub,
#         '*': mul,
#         '/': truediv,
#     }
#     query = re.sub(r'\s+', '', query)
#     if query.isdigit():
#         return float(query)
#     for c in operators.keys():
#         left, operator, right = query.partition(c)
#         if operator in operators:
#             return round(operators[operator](calculator(left), calculator(right)),2)


# %%
def calculator(query: str):
    import sympy
    return round(float(sympy.sympify(query)),2)
# %%
