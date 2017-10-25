class Fagin:

    def sort_lists(self,posting_list):
        ordered_list = []
        for  posting_list_line in posting_list:
            ordered_list.append(sorted(posting_list_line, key=lambda tup: tup[1], reverse=True))
        return ordered_list

    def fagin(self,posting_list , k):
        M = {}
        C = []

        ordered_list = self.sort_lists(posting_list)
        len_lists = len(ordered_list)
        for i in range(0, k):
            for ordered_list_line in ordered_list:
                doc_id, score = ordered_list_line[i]
                if doc_id in M:
                    M[doc_id] = [(M[doc_id][0] + score), (M[doc_id][1] + 1)]
                    if M[doc_id][1] == len_lists:
                        C.append((doc_id, (M[doc_id][0]) / M[doc_id][1]))
                        M.__delitem__(doc_id)
                else:
                    M[doc_id] = [score, 1]

        for x in M:
            for ordered_list_line in ordered_list:
                doc = next((doc for doc in ordered_list_line[k:] if doc[0] == x), -1)
                if doc != -1:
                    M[x] = [(M[x][0] + doc[1]), (M[x][1] + 1)]
                    if M[x][1] == len_lists:
                        C.append((x, (M[x][0]) / M[x][1]))

        R = sorted(C, key=lambda tup: tup[1], reverse=True)[0:k]

        return R