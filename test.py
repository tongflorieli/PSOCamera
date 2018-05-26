test = [1,0]

def outer(test):
    if test[0] == 1:
        test[1] = 2
    else:
        test = 3

outer(test)
print(test)