#!/usr/bin/env python
import os
import sys, getopt

#script para llamarlo desde la consola (CLI) y hacer lo que hacia con app.py
print("Oikaze Jinja")

helpText = """
--server || -s: to serve an HTTP server on local (default :9000)


"""

def test(args = False):
    print("Running " + args)


def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("ERROR parsing the arguments")
        print(helpText)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h' or "--help":
            print(helpText)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        else:
            print("Unknown: " + opt )

    print( 'Input file is "', inputfile)
    print('Output file is "', outputfile)



def runArgs():
    args = sys.argv
    args.pop(0)  # drop first ele: file name

    print(" ".join(args))
    func = args[0]
    args.pop(0) # drop func name
    #args = " ".join(args )
    try:
        if args:
            r = exec(func + "(*" + args + ")")
        else:
            r = exec(func + "()")
    except:
        print("Oops!", sys.exc_info()[0], "occurred.")
        print("Error can't run: ", func, "(", args, ")")
        sys.exit(2)
    return r

#runArgs()


if __name__ == "__main__":
   main(sys.argv[1:])


