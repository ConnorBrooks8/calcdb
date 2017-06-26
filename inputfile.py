#!/usr/bin/python3
import sys
import dbobjects as db
filename=sys.argv[1]
Database1 = db.Database(filename)
Database1.inputfile(filename)
