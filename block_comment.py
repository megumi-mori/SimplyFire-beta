len_sharp = 50
while(True):
    word = input("comment:")

    print('#'*len_sharp)
    num_space = len_sharp - len(word)-2
    if num_space % 2 == 0:
        print(('#'+" "*int(num_space/2) + word + " "*int(num_space/2)+"#"))
    else:
        print(('#'+" "*int((num_space)/2) + word + " "*int((num_space)/2+1) +"#"))
    print('#'*len_sharp)