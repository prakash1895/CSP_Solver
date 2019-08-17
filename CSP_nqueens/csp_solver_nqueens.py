from collections import defaultdict
import numpy as np
import sys
import copy
import matplotlib.pyplot as plt
import time
from plot_nqueens import plot_nqueens

class CSP_variable:
    def __init__(self, queen_id, n):
        self.id = queen_id
        self.permissible_values = sorted([(i,queen_id) for i in range(n)])
        self.arc_neighbors = sorted(list(set(range(n)) - set([queen_id])))

class CSP_Solver:
    def __init__(self, nqueens):
        self.nqueens = nqueens
        self.var_dict = {}
        
        for queen_id in range(nqueens):
            self.var_dict[queen_id] = CSP_variable(queen_id, nqueens)

    def solve(self):
        print ""
        start = time.time()
        assignments = {}
        unassigned = {queen_id: csp_var.permissible_values for queen_id, csp_var in self.var_dict.iteritems()}
        unassigned = self.AC3_consistency(assignments, unassigned)
        result = self.backtrack(assignments, unassigned)
        time_taken = time.time() - start
        self.print_result(result, time_taken)
        return time_taken

    def print_assignment(self, assignments):
        print "Current Assignment"
        if bool(assignments) == False:
            print "{Empty State}"
            print ""
            return

        for var, pv in assignments.iteritems():
            print var, pv[0]
        print ""

    def break_symmetry(self, CM):
        CM_list = []
        CM_list.append(CM)
        CM_list.append(np.rot90(CM, 1)) 
        CM_list.append(np.rot90(CM, 2))
        CM_list.append(np.rot90(CM, 3))
        CM_list.append(np.fliplr(CM))
        CM_list.append(np.flipud(CM))
        CM_list.append(np.transpose(CM))
        return CM_list

    def print_result(self, result, time_taken):
        if result == False:
            print "\n------------------------------------------\n"
            print "CSP Assignment Failure!\n"
            print "Time Taken (sec): ", time_taken
        else:
            self.print_assignment(result)
            print "------------------------------------------\n"
            print "CSP Assignment Success!\n"
            Q_matrix = np.zeros((self.nqueens, self.nqueens))
            for var in result.keys():
                val = result[var][0]
                i = val[0]
                j = val[1]
                Q_matrix[i][j] = 1

            print "Time Taken (sec): ", time_taken
            title=str(self.nqueens)+"-Queens"
            print "\n------------------------------------------\n"

            CM_list = self.break_symmetry(Q_matrix)
            plot_nqueens(CM_list[0], self.nqueens, title=title+" Original")
            plot_nqueens(CM_list[1], self.nqueens, title=title+" rot90")
            plot_nqueens(CM_list[2], self.nqueens, title=title+" rot180")
            plot_nqueens(CM_list[3], self.nqueens, title=title+" rot270")
            plot_nqueens(CM_list[4], self.nqueens, title=title+" Flip Horizontally")
            plot_nqueens(CM_list[5], self.nqueens, title=title+" Flip Vertically")
            plot_nqueens(CM_list[6], self.nqueens, title=title+" Flip Diagonally")
            
    def check_constraint(self, Qi_pos, Qj_pos):
        if Qi_pos[0] == Qj_pos[0]: # Row-Constraint
            return False

        elif Qi_pos[1] == Qj_pos[1]: # Column-Constraint
            return False

        elif abs(Qi_pos[0] - Qj_pos[0]) == abs(Qi_pos[1] - Qj_pos[1]): # Diagonal-Constraint
            return False

        else:
            return True

    def remove_inconsistent_values(self, arc, unassigned):
        Qi = arc[0]
        Qj = arc[1]
        removed = False
        reduced_domain = []
        for Qi_pos in unassigned[Qi]:
            for Qj_pos in unassigned[Qj]:
                if self.check_constraint(Qi_pos, Qj_pos) and Qi_pos not in reduced_domain:
                    reduced_domain.append(Qi_pos)
        
        if len(reduced_domain) != len(unassigned[Qi]):
            removed = True
            unassigned[Qi] = reduced_domain
        return unassigned, removed

    def create_arc_queue(self, unassigned):
        arc_queue = []
        for Qi in unassigned.keys():
            for Qj in self.var_dict[Qi].arc_neighbors:
                if (Qi,Qj) not in arc_queue and (Qj,Qi) not in arc_queue:
                    arc_queue.append((Qi,Qj))
        return arc_queue

    def AC3_consistency(self, assignments, unassigned):
        arc_queue = self.create_arc_queue(unassigned)
        updated_assignment = unassigned.copy()
        updated_assignment.update(assignments)
        while len(arc_queue) != 0:
            (Qi, Qj) = arc_queue.pop(0)
            updated_assignment, removed = self.remove_inconsistent_values((Qi, Qj), updated_assignment)
            if removed == True:
                for Qk in self.var_dict[Qi].arc_neighbors:
                    if (Qk, Qi) not in arc_queue:
                        arc_queue.append((Qk, Qi))
        return updated_assignment

    def check_complete(self, unassigned):
        if len(unassigned) == 0:
            return True
        return False

    def select_unassigned_variable(self, unassigned):
        mrv_dict = {k: len(unassigned[k]) for k in unassigned.keys()}
        mrv_var = min(mrv_dict, key=mrv_dict.get)
        return mrv_var

    def count_vals(self, updated, var):
        cnt = sum((len(updated[v]) for v in updated if v!=var))
        return cnt

    def order_domain_values(self, var, assignments, unassigned):
        lcv_dict = {}
        for val in unassigned[var]:
            assignments[var] = [val]
            updated = self.AC3_consistency(assignments, unassigned)
            n_constraints = self.count_vals(updated, var)
            lcv_dict[val] = n_constraints
            del assignments[var]
        lcv_list = sorted(lcv_dict, key=lcv_dict.get, reverse=True)
        return lcv_list

    def is_empty(self, v):
        for values in v.itervalues():
            if len(values) == 0:
                return True
        return False

    def backtrack(self, assignments, unassigned):
        if self.check_complete(unassigned):
            return assignments

        var = self.select_unassigned_variable(unassigned)
        values = self.order_domain_values(var, assignments, unassigned)
        del unassigned[var]
        self.print_assignment(assignments)
        
        for value in values:    
            assignments[var] = [value]
            updated_assignment = self.AC3_consistency(assignments, unassigned)
            if self.is_empty(updated_assignment):
                continue
            revised = {var:val for var,val in updated_assignment.iteritems() if var not in assignments}
            result = self.backtrack(assignments.copy(), revised)
            if result != False:
                return result
        return False
        
if __name__ == '__main__':
    if len(sys.argv) < 2:
        nqueens = 8
        print "\nNumber of Queens not specified!"
        print "Taking N=8 by default. \n"
    else:
        nqueens = int(sys.argv[1])
    csp_obj = CSP_Solver(nqueens)
    time_taken = csp_obj.solve()

