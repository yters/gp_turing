from math import log, ceil
from random import randint, random, choice
import sys

# Class defines the P'' (P double prime) language with the additional I/O commands.
# The P'' language is a minimal Turing complete language consisting of just 8 command characters, plus the end of program character 'E'.
# One important thing to note about P'' is that every string of symbols is a valid program (although most do a lot of useless operations).
# Random code and input are also added during execution if the code or input pointers exceed the end of the current tape.  The purpose of the random additions is to discover what randomly generated programs can do, by initializing a run with an empty code and input string, i.e. the default values.
class Pm():
    def __init__(self, code = [], iput = []):
        # Setup the tapes, pointers and counters.
        self.code_bitstring = [symbol for symbol in code]
        self.data_bitstring = [0]
        self.iput_bitstring = [b for b in iput]
        self.oput_bitstring = []

        self.code_pntr = 0
        self.data_pntr = 0
        self.iput_pntr = 0

        self.left_brace_counter = 0
        self.right_brace_counter = 0

        # Map the command symbols to the class method.
        # Explaining these commands requires background on the P'' execution machine.
        # The machine has four tapes: input, output, code, and data.
        # The code tape consists of special symbols.
        # The input, output, and data tapes consist of integers between 0 and 255.
        # The execution only reads from input, and writes to output, sequentially.
        # The execution only reads from code, but not necessarily sequentially.  The jump and back commands allow non sequential code traversal based on markers.
        # The data tape is traversed incrementally forward and backwards, with no jumping.  The data tape consists only of integers between 0 and 255.  The integers can be incremented and decremented.  If the data pointers exceeds the end of the tape, a new cell is added with value 0.
        # The input read operation writes the integer in the current input tape cell to the current data tape cell, and then pops the input cell.
        # The output write operation appends the integer in the current data tape cell to the output tape.
        self.c2m = {
            ">":self.inc_data_ptr, # Move one step right along the data tape. If progresses past the end, then add a new cell to the data tape initialized with 0.
            "<":self.dec_data_ptr, # Move one step left along th edata tape. Cannot progress past the beginning.
            "-":self.dec_byte, # Decrement the current data cell integer by one.  Cannot go below 0.
            "+":self.inc_byte, # Increment the current data cell integer by one.  Cannot go above 255.
            "[":self.jump, # Conditionally jump forward to the next matching ']'.  Matching is determined based on nested brackets' level.
            "]":self.back, # Conditionally jump backward to the previous matching '['.
            ".":self.oput, # Append current data cell integer to the current output cell.
            ",":self.iput  # Pop current input cell integer to the current data cell.
        }

        self.symbols = list(self.c2m.keys()) + ["E"] # Add the program end symbol to list of possible symbols.

        # A reduced class of symbols used to evolve programs without input and without a set end.
        self.symbols_minus_input_and_end = [symb for symb in self.symbols]
        self.symbols_minus_input_and_end.remove(",")
        self.symbols_minus_input_and_end.remove("E")

    # The following two random addition methods are used to generate random extensions to the code and data strings, to allow the generation of random programs.
    def add_random_symbol(self, jumping):
        self.code_bitstring += [self.symbols[randint(0,len(self.symbols)-1-int(jumping))]]

    def add_random_byte(self):
        self.iput_bitstring += [randint(0,255)]

    # The following are the language commands.
    # Most commands only return True.  The two exceptions are the jump and input commands.  Reason being these commands can exceed the end of the code and input tape, respectively, requiring the addition of new information.
    def inc_data_ptr(self):
        self.data_pntr += 1
        if self.data_pntr == len(self.data_bitstring):
            self.data_bitstring += [0]
        return True

    def dec_data_ptr(self):
        if self.data_pntr > 0:
            self.data_pntr -= 1
        return True

    def inc_byte(self):
        if self.data_bitstring[self.data_pntr] < 255:
            self.data_bitstring[self.data_pntr] = self.data_bitstring[self.data_pntr] + 1
        return True

    def dec_byte(self):
        if self.data_bitstring[self.data_pntr] > 0:
            self.data_bitstring[self.data_pntr] = self.data_bitstring[self.data_pntr] - 1
        return True

    # The jump and back commands are conditional.
    # The jump command jumps forward only if the current data cell is zero.
    # The back command jumps backward only if the current data cell is not zero.
    # This allows for conditional logic in the P'' language, similar to the IF ... THEN GOTO ... command in BASIC.
    def jump(self):
        self.left_brace_counter += 1
        if self.data_bitstring[self.data_pntr] == 0:
            while not self.left_brace_counter == 0:
                if self.code_pntr + 1 >= len(self.code_bitstring):
                    return False
                self.code_pntr += 1
                if self.code_bitstring[self.code_pntr] == "[":
                    self.left_brace_counter += 1
                elif self.code_bitstring[self.code_pntr] == "]":
                    self.left_brace_counter -= 1
        return True

    def back(self):
        self.right_brace_counter += 1
        if not self.data_bitstring[self.data_pntr] == 0:
            while not self.right_brace_counter == 0:
                if self.code_pntr - 1 == 0:
                    return True
                self.code_pntr -= 1
                if self.code_bitstring[self.code_pntr] == "[":
                    self.right_brace_counter -= 1
                elif self.code_bitstring[self.code_pntr] == "]":
                    self.right_brace_counter += 1
        return True

    def oput(self):
        self.oput_bitstring += [self.data_bitstring[self.data_pntr]]
        return True

    def iput(self):
        if self.iput_pntr < len(self.iput_bitstring):
            self.data_bitstring[self.data_pntr] = self.iput_bitstring[self.iput_pntr]
            self.iput_pntr += 1
            return True
        return False

    # The executor is responsible for the running of the program.
    # It produces a generator, so that the program can be run a step at a time.
    # This way the number of execution steps can be externally limited.
    # There is special logic to handle forward jumps, since the jumps can go past the end of programs, and new information needs to be added to the program.
    def ex(self):
        self.code_pntr = 0
        jumping = False
        while True:
            if self.code_pntr >= len(self.code_bitstring)-1:
                self.add_random_symbol(jumping)
            if self.iput_pntr == len(self.iput_bitstring):
                self.add_random_byte()

            if self.code_bitstring[self.code_pntr] == "E":
                break
            if jumping:
                jumping = self.jump()
            elif self.c2m[self.code_bitstring[self.code_pntr]]():
                self.code_pntr += 1
            else:
                jumping = True
            yield True

# The following section creates the genetic programming operators to evolve programs, along with the parameter settings.
# There are just two operators that modify the code in the programs, but they are sufficiently general to cover every kind of genetic operation known to modern evolutionary theory.
# Also important is these operators are random in the Darwinian sense.  They do not operate with any knowledge of the meaning of the code, nor of the fitness function.

# The mutation operator is the fundamental source of new genetic material, as well as destruction of genetic material.
# Most importantly, mutation can add a new cell with a random symbol to the code bitstring, which is necessary to get started from nothing.  The probability of a new symbol being added for each possible addition point in the code tape is defined in the following parameter.
prob_add = 0.1
# The other two mutations are:
# 1. flipping an arbitrary symbol in the code tape
# 2. deleting a cell in the code tape
# Their corresponding probabilities per application site are the following parameters.
prob_flip = 0.1
prob_del = 0.1

# Need an instance to accesss the symbols.
pm = Pm()
def mutate(ind):
    new_ind = []
    curr_pos = 0
    while curr_pos <= len(ind):
        if random() < prob_del:
            curr_pos += 1
        elif random() < prob_add:
            new_ind += [choice(pm.symbols_minus_input_and_end)]
        elif random() < prob_flip:
            new_ind += [choice(pm.symbols_minus_input_and_end)]
            curr_pos += 1
        elif curr_pos < len(ind):
            new_ind += [ind[curr_pos]]
            curr_pos += 1
        else:
            curr_pos += 1
    return new_ind

# The crossover function allows genetic material to be shared within a population.
# It takes two individuals from the population, and for each selects two random cut points.
# A new individual is generated by removing the cut material from the first individual and replacing with the cut material from the second individual.
# The important thing to note about this operator is that it is general enough to represent all forms of genetic material transferral considered in modern evolutionary theory.
def crossover(indA, indB):
    if len(indA) == 0:
        return []
    if len(indB) == 0:
        return [symb for symb in indA]
    indA_start, indA_end = sorted([randint(0, len(indA)-1), randint(0, len(indA)-1)])
    indB_start, indB_end = sorted([randint(0, len(indB)-1), randint(0, len(indB)-1)])
    return indA[0:indA_start] + indB[indB_start:indB_end] + indA[indA_end:]

# The fitness function is the key for selection.
# It runs a program for a set number of steps, to avoid infinite loops.
# Then, the fitness function compares the output of the program against the target using the sum of absolute difference.
# In the case the output string is not the same length as the target string, the difference is padded with zeroes.
fitness_steps = 0 # Count how many program steps are needed to find the solution.
max_fitness_steps_per_exec = 100 # Number of fitness steps each program is allowed to run.

# Target defaults to counting from 0 to 2, but allows an end to be set by comamndline for experimenting.
def eval(ind):
    global fitness_steps
    # Initialize generator to run code.
    code = [symb for symb in ind] + ["E"] # Add termination to code.
    tm = Pm(code=code)
    tm_iter = tm.ex()

    # Run code for set number of steps.
    for _ in range(max_fitness_steps_per_exec):
        try:
            fitness_steps += 1
            next(tm_iter)
        except StopIteration:
            return tm.oput_bitstring
    return None # Treat code like infinite loop that never returns

# Return the code fitness.
def fitness(ind, target):
    oput_bitstring = eval(ind)
    if oput_bitstring:
        return sum([abs(o-n) for o, n in zip(oput_bitstring, target)]) + abs(len(target)-len(oput_bitstring))
    else:
        return float('inf')

if __name__ == "__main__":
    # Setup the experiments
    experiments = []
    experiments_log = []
    num_trials = 10
    param = 0

    # Setup results files
    open('hof.txt', 'w').close()
    hof_file = open('hof.txt', 'a')
    open('stats.txt', 'w').close()
    stats_file = open('stats.txt', 'a')
    
    # Run experiments indefinitely until keyboard interrupt is called.
    try:
        everything_is_fine = True
        while everything_is_fine:
            param += 1
            experiments += [param]
            target = list(range(param))
            trials_log = [] # Log to calculate stats.
            for trial in range(num_trials):
                pop_size = 100 # The population size.  Each generation, population is dropped back to this size.
                pop = [[]] * pop_size # Each member of the population starts empty.
                gen_size = 100 # Number of new individuals to create each generation.
    
                fitness_steps = 0 # Reset fitness counter.
                best_fitness = float('inf')
                found = False
                max_generations = 10000 # Evolve for a set number of generations.
                for i in range(max_generations):
                    # Create the new generation.
                    for _ in range(gen_size):
                        child = mutate(crossover(choice(pop), choice(pop)))
                        pop += [child]
            
                    # Cull the population.
                    pop = sorted(pop, key=lambda x: fitness(x, target=target))[:pop_size]
            
                    # Print out new advances in the population.
                    if fitness(pop[0], target) < best_fitness:
                        best_fitness = fitness(pop[0], target=target)
                        print('---------')
                        print('iteration: ' + str(i))
                        print('trial: ' + str(trial))
                        print('target: ' + '|'.join([str(d) for d in target]))
                        print('fitness: ' + str(best_fitness))
                        print('length: ' + str(len(pop[0])))
                        print('code: ' + ''.join(pop[0]))
                        print('output: ' + '|'.join([str(d) for d in eval(pop[0])]))
            
                    # Check for success finding the target.
                    if fitness(pop[0], target) == 0:
                        found = True
                        print('success!')
                        code_str = ''.join(pop[0])
                        hof_file.write(str(param) + ' ' + str(trial) + ' ' + str(fitness_steps) + ' ' + code_str + '\n')
                        hof_file.flush()
                        inductee = (param, trial, fitness_steps, code_str)
                        break
            
                if not found:
                    print('after ' + str(max_generations) + ' generations did not find this solution: ' + str(target))
                    everything_is_fine = False
            
                print('number of execution steps spent evolving: ' + str(fitness_steps))
                trials_log += [fitness_steps]
                if not everything_is_fine:
                    break
            avg_steps = sum(trials_log)/float(num_trials)
            stats_file.write(str(avg_steps) + '\n')
            stats_file.flush()
            experiments_log += [avg_steps]
    except KeyboardInterrupt:
        pass

    hof_file.close()
    stats_file.close()
    
    for param, avg_steps in zip(experiments, experiments_log):
        print('for experiment param ' + str(param) + ' took average of ' + str(int(avg_steps)) + ' steps to find solution.')

