

def addition(a,b):
    return a+b

def mult(a,b):
    return a*b


def calculate(calc_function, a, b):
    return calc_function(a,b)


x = calculate(addition, 5, 6)

print(x)

