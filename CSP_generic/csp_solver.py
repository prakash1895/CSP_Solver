from collections import defaultdict
import numpy as np
import sys
import copy

class CSP_variable:
	def __init__(self, name, task_length, values):
		self.name = name
		self.task_length = task_length
		self.permissible_values = sorted(values)
		self.arc_neighbors = []

class CSP_value:
	def __init__(self, name, key):
		self.name = name
		self.key = key
		self.time_taken = 0.0
		self.cost = 0.0

class CSP_Solver:
	def __init__(self, filename, cost=None):
		self.var_dict = {}
		self.value_dict = {}
		self.deadline = 0.0
		self.constraint_matrices = []
		self.read_txt(filename)
		self.print_constraints()

		if cost == None:
			self.optional = False
		else:
			self.optional = True
			self.read_costfile(cost)

		constraints = copy.deepcopy(self.constraint_matrices)
		assignments = {}
		unassigned = {var: v.permissible_values for var, v in self.var_dict.iteritems()}
		unassigned = self.AC3_consistency(unassigned, constraints)
		result = self.backtrack(assignments, unassigned, constraints)
		self.print_result(result)

	def print_result(self, result):
		print ""
		print "------------------------------------------"
		
		if result == False:
			print "CSP Assignment Failure!"
			print ""
		else:
			print "CSP Assignment Success!\n"
			print "Task\tProcessor"
			for k,v in sorted(result.iteritems()):
				print "  " + str(k) + "\t   " + str(v)
			print ""

			max_time = 0.00
			print "Processor\tTotal Run Time"
			for k,v in sorted(self.value_dict.iteritems()):
				print "   " + str(k) + "\t\t     " + str(v.time_taken)
				if v.time_taken >= max_time:
					max_time = v.time_taken
			print ""
			print "Total Length of All Tasks: ", max_time
			print ""

			if self.optional == True:
				total_cost = 0.00
				print "Processor\tCost"
				for k,v in sorted(self.value_dict.iteritems()):
					p_cost = v.time_taken*v.cost
					total_cost += p_cost
					print "   " + str(k) + "\t\t" + str(p_cost)
				print ""
				print "Total Cost of All Tasks: ", total_cost
				print ""

	def read_costfile(self, costfile):
		lines = [line.rstrip() for line in open(costfile)]
		for line in lines:
			words = line.split()
			value = words[0]
			cost = float(words[1])

			if value in self.value_dict.keys():
				self.value_dict[value].cost = cost

	def read_txt(self, filename):
		hash_list = []
		lines = [line.rstrip() for line in open(filename)]
		for i in range(len(lines)):
			if lines[i][:5] == '#####':
				hash_list.append(i)
		
		var_lines = lines[hash_list[0]+1:hash_list[1]]
		values_lines = lines[hash_list[1]+1:hash_list[2]]
		deadline_lines = lines[hash_list[2]+1:hash_list[3]]
		un_incl_lines = lines[hash_list[3]+1:hash_list[4]]
		un_excl_lines = lines[hash_list[4]+1:hash_list[5]]
		bin_equal_lines = lines[hash_list[5]+1:hash_list[6]]
		bin_uneq_lines = lines[hash_list[6]+1:hash_list[7]]
		bin_sim_lines = lines[hash_list[7]+1:]

		self.deadline = float(deadline_lines[0])

		values = sorted(values_lines)
		key = 0
		for value in values:
			value_obj = CSP_value(value, key)
			self.value_dict[value] = value_obj
			key += 1

		for var_line in var_lines:
			words = var_line.split()
			name = words[0]
			task_length = float(words[1])
			var_obj = CSP_variable(name, task_length, values)
			self.var_dict[name] = var_obj

		for un_incl_line in un_incl_lines:
			words = un_incl_line.split()
			var_name = words[0]
			incl_list = [value for value in words[1:]]
			if len(incl_list)!= 0:
				self.var_dict[var_name].permissible_values = sorted(incl_list)

		for un_excl_line in un_excl_lines:
			words = un_excl_line.split()
			var_name = words[0]
			excl_list = [value for value in words[1:]]
			if len(excl_list) != 0:
				permissible_values = list(set(self.var_dict[var_name].permissible_values) - set(excl_list))
				self.var_dict[var_name].permissible_values = sorted(permissible_values)

		for bin_equal in bin_equal_lines:
			words = bin_equal.split()
			var1 = words[0]
			var2 = words[1]
			m, bin_mat = self.create_binary_constraint_matrix(var1, var2)
			for i in range(m):
				for j in range(m):
					if i != j:
						bin_mat[i,j] = 0

			self.var_dict[var1].arc_neighbors.append(var2)
			self.var_dict[var2].arc_neighbors.append(var1)

			self.constraint_matrices.append([var1, var2, bin_mat])
			self.constraint_matrices.append([var2, var1, np.transpose(bin_mat)])

		for bin_uneq in bin_uneq_lines:
			words = bin_uneq.split()
			var1 = words[0]
			var2 = words[1]
			m, bin_mat = self.create_binary_constraint_matrix(var1, var2)
			for i in range(m):
				for j in range(m):
					if i == j:
						bin_mat[i,j] = 0

			self.var_dict[var1].arc_neighbors.append(var2)
			self.var_dict[var2].arc_neighbors.append(var1)

			self.constraint_matrices.append([var1, var2, bin_mat])
			self.constraint_matrices.append([var2, var1, np.transpose(bin_mat)])
			
		for bin_sim in bin_sim_lines:
			words = bin_sim.split()
			var1, var2 = words[0], words[1]
			
			m, bin_mat = self.create_binary_constraint_matrix(var1, var2)
			key1, key2 = self.value_dict[words[2]].key, self.value_dict[words[3]].key
			bin_mat[key1, key2] = 0

			self.var_dict[var1].arc_neighbors.append(var2)
			self.var_dict[var2].arc_neighbors.append(var1)

			self.constraint_matrices.append([var1, var2, bin_mat])
			self.constraint_matrices.append([var2, var1, np.transpose(bin_mat)])

	def create_binary_constraint_matrix(self, var1, var2):
		values = sorted(self.value_dict.keys())
		m =len(values)
		bin_mat = np.ones((m,m), dtype=np.uint8)
		for val_excl in list(set(values) - set(self.var_dict[var1].permissible_values)):
			key = self.value_dict[val_excl].key
			bin_mat[key,:] = 0

		for val_excl in list(set(values) - set(self.var_dict[var2].permissible_values)):
			key = self.value_dict[val_excl].key
			bin_mat[:,key] = 0
		return m, bin_mat

	def print_constraints(self):
		print ""
		print "Binary Constraint Matrices"
		print ""
		for head_var, tail_var, matrix in self.constraint_matrices:
			print head_var+tail_var+" Matrix"
			print matrix
			print ""
		print "------------------------------------------"

	def remove_inconsistent_values(self, arc, unassigned, matrix):
		Xi = arc[0]
		Xj = arc[1]
		removed = False
		reduced_domain = []
		for value in unassigned[Xi]:
			key = self.value_dict[value].key
			row_vec = matrix[key, :]
			if (np.count_nonzero(row_vec)) != 0:
				reduced_domain.append(value)

		if len(reduced_domain) != len(unassigned[Xi]):
			removed = True
			unassigned[Xi] = reduced_domain
		return unassigned, removed
	
	def create_arcs_dict(self, constraints):
		arc_queue = []
		arc_matrices = {}
		for xi, xj, matrix in constraints:
			arc_queue.append((xi,xj))
			arc_matrices[xi+xj] = matrix
		return arc_queue, arc_matrices

	def AC3_consistency(self, unassigned, constraints):
		arc_queue, arc_matrices = self.create_arcs_dict(constraints)
		while len(arc_queue) != 0:
			(xi, xj) = arc_queue.pop(0)
			matrix = arc_matrices[xi+xj]
			unassigned, removed = self.remove_inconsistent_values((xi, xj), unassigned, matrix)
			if removed == True:
				for xk in self.var_dict[xi].arc_neighbors:
					if (xk, xi) not in arc_queue:
						arc_queue.append((xk, xi))
		return unassigned

	def check_complete(self, unassigned):
		if len(unassigned) == 0:
			return True
		return False

	def degree_heuristic(self, mrv_list):
		degree_list = []
		for var in mrv_list:
			n_constraints = len(self.var_dict[var].arc_neighbors)
			degree_list.append((n_constraints,var))

		degree_list = sorted(degree_list)
		var = degree_list[-1][1]
		return var

	def select_unassigned_variable(self, unassigned):
		if self.optional == False:
			mrv_dict = defaultdict(list)
			for var in sorted(unassigned.keys()):
				mrv_key = len(unassigned[var])
				mrv_dict[mrv_key].append(var)

			mrv_list = mrv_dict[sorted(mrv_dict.keys())[0]]
			if len(mrv_list) == 1:
				mrv_variable = mrv_list[0]
			else:
				mrv_variable = self.degree_heuristic(mrv_list)
			return mrv_variable 

		else:
			mrv_list = sorted([(self.var_dict[k].task_length, k) for k in unassigned.keys()], reverse=True)
			mrv_variable = mrv_list[0][1]
			return mrv_variable

	def order_domain_values(self, var, unassigned, constraints):
		if self.optional == False:
			valid_values = unassigned[var]
			lcv_dict = {}
			for val in valid_values:
				lcv_dict[val] = 0

			for head_var, tail_var, matrix in constraints:
				if var == head_var:
					for value in valid_values:
						n_cons = 0
						key = self.value_dict[value].key
						value_vec = matrix[key,:]
						lcv_dict[value] += np.count_nonzero(value_vec)

			lcv_list = sorted(lcv_dict.keys(), key=lcv_dict.get)
			return lcv_list

		else:
			valid_values = unassigned[var]
			lcv_cost_list = sorted([(self.value_dict[k].cost, k) for k in valid_values])
			lcv_list = [v for c,v in lcv_cost_list]
			return lcv_list

	def make_assignment(self, var, value, assignments, unassigned):
		assignments[var] = value
		del unassigned[var]
		self.value_dict[value].time_taken += self.var_dict[var].task_length
		return assignments

	def undo_assignment(self, var, value, assignments, unassigned):
		del assignments[var]
		unassigned[var] = self.var_dict[var].permissible_values
		self.value_dict[value].time_taken -= self.var_dict[var].task_length
		return assignments

	def propagate_constraints(self, assignments, constraints):
		constraints_modified = copy.deepcopy(constraints)
		for head_var, tail_var, matrix in constraints_modified:
			if head_var in assignments.keys():
				assigned_value = assignments[head_var]
				key = self.value_dict[assigned_value].key
				for i in range(len(matrix)):
					if i != key:
						matrix[i,:] = 0

			if tail_var in assignments.keys():
				assigned_val = assignments[tail_var]
				key = self.value_dict[assigned_val].key
				for i in range(len(matrix)):
					if i != key:
						matrix[:,i] = 0
		return constraints_modified

	def is_empty(self, constraints):
		for head_var, tail_var, matrix in constraints:
			if (np.count_nonzero(matrix)) == 0:
				return True
		return False

	def backtrack(self, assignments, unassigned, constraints):
		if self.check_complete(unassigned):
			return assignments

		var = self.select_unassigned_variable(unassigned)
		values = self.order_domain_values(var, unassigned, constraints)

		print ""
		print "Assignment: ", assignments
		print "Variable Attempt: ", var
		print "permissible_values: ", values
		constraints_old = copy.deepcopy(constraints)
		for value in values:
			print "Value Attempt: ", value
			if (self.value_dict[value].time_taken + self.var_dict[var].task_length) <= self.deadline:
				assignments = self.make_assignment(var, value, assignments, unassigned)
				constraints = self.propagate_constraints(assignments, constraints)
				if self.is_empty(constraints):
					assignments = self.undo_assignment(var, value, assignments, unassigned)
					constraints = constraints_old
					continue
				result = self.backtrack(assignments, unassigned, constraints)
				if result != False:
					return result
				assignments = self.undo_assignment(var, value, assignments, unassigned)
				constraints = constraints_old
		return False
		
if __name__ == '__main__':
	filename = sys.argv[1]
	cost_file = None
	if len(sys.argv) > 2:
		cost_file = sys.argv[2]
	csp_obj = CSP_Solver(filename, cost=cost_file)
	
	