#! /usr/bin/env python3
# Manuel Ruvalcaba
# Theory of Operating Systems
# Shell lab
# This lab is a mini-shell that is supposed to mimic bash shell

import os, sys, time, re 
from myread import myReadLines
from redirect import hasRedirect, validateRedirect

pid = os.getpid()

def main():
    while(1):
        os.write(1, '$ '.encode())    
        args = myReadLines().split() # get user input and tokenize in one line
        if(args == []):                # if there was no input, continue to the next loop
            continue
        elif args[0] == "exit":        # if command is 'exit', the shell will close
            sys.exit(1)
        elif args[0] == "cd":          # changes current directory
            if(len(args) == 1):
                os.chdir("..")
            else:
                os.chdir(args[1])
            continue;
        rc = os.fork()                 # forks a child
        if rc < 0:                     # if rc is negative, fork failed
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        
        elif rc == 0: # if rc == 0, it is the child
            if(hasRedirect(args)):  
                valid, inputRed, outputRed, args = validateRedirect(args) # validates the redirects
                if(valid == False):
                    os.write(2, ("Invalid Redirect formatting. \n").encode())
                    sys.exit(1)
                if(inputRed is not ""):                                  # if no input Redirect
                    os.close(0)
                    os.open(inputRed, os.O_RDONLY)
                    os.set_inheritable(0, True)
                if(outputRed is not ""):                                 # if no output Redirect
                    os.close(1)
                    os.open(outputRed, os.O_CREAT | os.O_WRONLY)
                    os.set_inheritable(1,True)
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly
            
            os.write(2, ("%s: Command not found \n" % args[0]).encode())
            sys.exit(1)                 # terminate with error
            
        else:                           # parent (forked ok)
            childPidCode = os.wait()    # waits for child process to finish

if __name__ == "__main__":
    main()
