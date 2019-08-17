# CSP Generic Solver
## WPI CS534 AI Project Part I

[Link to Project Instructions](http://web.cs.wpi.edu/~cs534/s19/Project/) 

### Instructions to run the code:

1) Open a new command terminal
2) Navigate to the project directory
3) Run the following command:
	* python csp_solver.py <filename> 
	* For example, python csp_solver.py map_coloring.txt

4) We also did a sub-optimal implementation for the optional part and included 2 files (test9 and test10) to test the implementation.
	* python csp_solver.py test9.txt test9_cost.txt

Sample Output:

<pre>
CSP Assignment Success!

 Task	Processor
  NSW	    g
  NT	    g
  Q	    b
  SA	    r
  T	    r
  V	    b
  WA	    b

Processor	Total Run Time
   b		      3.0
   g		      2.0
   r		      2.0

Total Length of All Tasks: 3.0
</pre>
