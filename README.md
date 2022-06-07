# Evolving Turing Complete Programs 

The script `gp_turing.py` illustrates the evolution of a Turing complete program to count sequential numbers.  The method of evolution involves both mutation and sharing of genetic information between members of the population to cover the full range of known genetic operators in biological evolutionary theory.  

To try out the program, simply run the script using Python3.  The script will run a set of experiments showing the evolution of longer and longer numerical sequences, until you press Ctrl-C, or the evolution process takes too long.  

At the end, it will print a summary of average execution steps needed for each experiment.  It will also create two output files: `stats.txt` and `hof.txt`.  Examples from a run I did are given in the repo.

The `stats.txt` file contains the average steps for each experiment.

The `hof.txt` file is more interesting.  It contains the "Hall of Fame" of the winning individual for each trial.  One interesting thing to note is how the pointless code bloat increases as the target sequence length increases.  This shows a general problem with evolution of programs with random mutation.  Since random numbers don't know anything about programming, using randomness to generate the program inevitably adds junk, and this happens more often the longer the programs are evolved.

For visualization, there is an R script `draw_ohno.r` that will create two plots to show the exponential time increase to evolve solutions as the sequence increases.

Here is the plot of the exponential increase.

![Graph showing exponential increase in time to evolve.](/ohno.png?raw=true "Exponential Evolution Time")

And a logarithmic plot to show the rate is clearly exponential. If a logarithmic plot shows a straight line, then the actual trend is exponential.  The chart shows a straight line, meaning for each increment in sequence length the evolutionary algorithm doubles the time to find a program to generate the sequence.

![Graph showing exponential increase in time to evolve, with log of y axis.](/ohno_log.png?raw=true "Exponential Evolution Time (Log Graph)")

The big takeaway is that evolutionary algorithms that use all known evolutionary mechanisms are unable to solve an extremely simple task in polynomial time.  This is bad news for evolution explaining the variety of life.
