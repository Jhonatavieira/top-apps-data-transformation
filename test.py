import array
# a = array.array('i', [1, 2, 3])
# for i in a:
#     print(i, end=' ')  # OUTPUT: 1 2 3
# OUTPUT: TypeError: an integer is required (got type str)
a = array.array('i', [1, 2, 'string'])
# a = [1, 2, 'string']
for i in a:
    print(i, end=' ')
