class Naive:

    def sort_lists(self, posting_list):
        ordered_list = []
        for posting_list_line in posting_list:
            ordered_list.append(sorted(posting_list_line, key=lambda tup: tup[1], reverse=True))
        return ordered_list

    def Naive(self,posting_list, k):
        S = {}
        C = []
        ordered_list = self.sort_lists(posting_list)
        len_lists = len(ordered_list)
        for i in range(0, k):
            for ordered_list_line in ordered_list:
                doc_id, score = ordered_list_line[i]
                if doc_id in S:
                    S[doc_id] += score
                else:
                    S[doc_id] = score

        for doc, score in S.items():
            C.append((doc, score / len_lists))

        R = sorted(C, key=lambda tup: tup[1], reverse=True)[0:k]

        return R
