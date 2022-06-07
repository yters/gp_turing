# Evolving Turing Complete Programs 

The script `gp_turing.py` illustrates the evolution of a Turing complete program to count sequential numbers.  The method of evolution involves both mutation and sharing of genetic information between members of the population to cover the full range of known genetic operators in biological evolutionary theory.  

To try out the program, simply run the script using Python3.  The script will run a set of experiments showing the evolution of longer and longer numerical sequences, until you press Ctrl-C, or the evolution process takes too long.  

At the end, it will print a summary of average execution steps needed for each experiment.  It will also create two output files: `stats.txt` and `hof.txt`.

The `stats.txt` file contains the average steps for each experiment.

The `hof.txt` file is more interesting.  It contains the "Hall of Fame" of the winning individual for each trial.  One interesting thing to note is how the pointless code bloat increases as the target sequence length increases.  This shows a general problem with evolution of programs with random mutation.  Since random numbers don't know anything about programming, using randomness to generate the program inevitably adds junk, and this happens more often the longer the programs are evolved.

For visualization, there is an R script `draw_ohno.r` that will create two plots to show the exponential time increase to evolve solutions as the sequence increases.
