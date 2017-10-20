
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

def Naive(List, k):
    S = {}
    C = []
    check_size_of_lists(List)
    check_lenght_of_lists(List)
    vocList = sort_lists(List)
    len_list = len(vocList)
    Nbr_list = len(vocList[0])
    print(str(vocList))
    for i in range(0, Nbr_list):

        for j in range(0, len_list):
            doc = vocList[j][i]
            if doc[0] in S:
                S[doc[0]] += doc[1]
            else:
                S[doc[0]] = doc[1]

    for item, mean in S.items():
        C.append((item, mean / Nbr_list))

    R = sorted(C, key=lambda tup: tup[1], reverse=True)[0:k]

    return R
