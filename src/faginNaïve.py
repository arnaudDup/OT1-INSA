def check_size_of_lists(vocList):
    try:
        if len(vocList) < 2:
            raise NameError("Number of list < 2")
    except NameError:
        print("Number of list < 2:(")
        raise


def check_lenght_of_lists(vocList):
    snitch = len(vocList[0])
    for list_t in vocList:
        try:
            if len(list_t) != snitch:
                raise NameError("The lists are different size")
        except NameError:
            print("The lists are different size :(")


def sort_lists(vocList):
    vocList_sorted = []
    for i, list_t in enumerate(vocList):
        vocList_sorted.append(sorted(list_t, key=lambda tup: tup[1], reverse=True))
    return vocList_sorted


def fagin_algorithme(List, k):
    M = {}
    C = []
    check_size_of_lists(List)
    check_lenght_of_lists(List)
    vocList = sort_lists(List)
    len_list = len(vocList)

    print(str(vocList))
    for i in range(0, k):
        for j in range(0, len_list):
            doc = vocList[j][i]
            if doc[0] in M:
                M[doc[0]] = [(M[doc[0]][0] + doc[1]), (M[doc[0]][1] + 1)]
                if M[doc[0]][1] == len_list:
                    C.append((doc[0], (M[doc[0]][0]) / M[doc[0]][1]))
                    M.__delitem__(doc[0])
            else:
                M[doc[0]] = [doc[1], 1]

    for x in M:
        for i in range(0, len_list):
            doc = next((doc for doc in vocList[i][k:] if doc[0] == x), -1)
            if doc != -1:
                M[x] = [(M[x][0] + doc[1]), (M[x][1] + 1)]
                if M[x][1] == len_list:
                    C.append((x, (M[x][0]) / M[x][1]))

    R = sorted(C, key=lambda tup: tup[1], reverse=True)[0:k]

    return R




