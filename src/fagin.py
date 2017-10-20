# --------------------------------------------------------------------------------
# Import
import sys
# --------------------------------------------------------------------------------
# Constant
SAVE_FILE  = 'saveFile'
# --------------------------------------------------------------------------------

def eprint(*args, **kwargs):
    #print(*args, file=sys.stderr, **kwargs)
    pass
    

#TODO(mathishammel): Use a real priority queue. Lists are disgusting
class TopEntries(object):
    def __init__(self, k):
        self.k = k
        self.top = []

    def insert(self, priority, element):
        self.top += [(priority, element)]
        self.top = sorted(self.top, reverse=True)[:self.k]

    def pop_lowest(self):
        res = self.top[-1]
        del self.top[-1]
        return res

    def get_min_score(self):
        if len(self.top) == 0:
            return -1.0
        return self.top[-1][0]

def calc_avg(lst):
    return float(sum(lst))/len(lst)

# Args :
# posting_lists is a list of PostingList objects corresponding to the PLs for all query terms.
# k is an integer containing the length of the desired top-k ranking
#
# Returns : A list containing the (total_score, doc_id) for the top-k elements
def top_k_thresh(posting_lists, k, epsilon=0.0):
    #Check if we're not trying to get an impossible top-k
    for posting_list in posting_lists:
        assert k < len(posting_list.ordered_list)

    top_k = TopEntries(k)
    top_non_visited = []
    for posting_list in posting_lists:
        top_non_visited.append(posting_list.seek_next())

    eprint('Initialized top inorder array :', top_non_visited)
    threshold = 1e999 # Close enough to infinity, hopefully...
    
    while top_k.get_min_score() < threshold / (1.0 + epsilon):
        eprint('Starting new round')
        selected_idx = -1
        best_indiv_in_order = -1.0 # Assuming all PL scores are positive
        eprint(top_non_visited)
        for idx, elem in enumerate(top_non_visited):
            score=elem[0]
            eprint(idx,score)
            eprint('Debug xx :',best_indiv_in_order,score)
            if best_indiv_in_order < score:
                selected_idx = idx
                best_indiv_in_order = score
        selected_element = top_non_visited[selected_idx]
        selected_score, selected_doc_id = selected_element
        eprint('  Selected PL index is', selected_idx)
        eprint('  Selected element is', selected_element)
        posting_lists[selected_idx].mark_visited(top_non_visited[selected_idx][1])
        top_non_visited[selected_idx] = posting_lists[selected_idx].seek_next()

        scores = []
        for idx in range(len(posting_lists)):
            if idx == selected_idx:
                scores.append(selected_score)
                continue
            scores.append(posting_lists[idx].random_lookup(selected_doc_id))
            posting_lists[idx].mark_visited(selected_doc_id)
            if top_non_visited[idx][1] == selected_doc_id:
                top_non_visited[idx] = posting_lists[idx].seek_next()
        
        eprint('  Individual scores for document',selected_doc_id,'are', scores)
        tot_score = calc_avg(scores)
        eprint('  Average score is', tot_score)
        top_k.insert(tot_score, selected_doc_id)
        eprint('  Current top K is', top_k.top)

        all_lists_ready = True
        next_prev_scores = []
        for idx,posting_list in enumerate(posting_lists):
            if posting_list.ordered_list[0][1] not in posting_list.docs_visited:
                eprint('  Posting list',idx,'is not ready for threshold computation yet, aborting.')
                all_lists_ready = False
                break
            next_prev_scores.append(posting_list.next_item_predecessor_score())
        eprint('  Nextprev scores are',next_prev_scores)
        if all_lists_ready:
            threshold = calc_avg(next_prev_scores)
    return top_k.top