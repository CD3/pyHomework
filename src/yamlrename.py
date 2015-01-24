#! /bin/env python


import yaml,sys,os,argparse,logging,dpath.util

logging.basicConfig( level=logging.DEBUG )

parser = argparse.ArgumentParser(description='rename some yaml file')
parser.add_argument('files', type=str, nargs='+', help='files to be renamed')
args = parser.parse_args()

for infile in args.files:
    try:
        data = {}
        with open(infile,'r') as f:
            data = yaml.load( f )


    except yaml.parser.ParserError, e:
        logging.error( "There was a problem parsing '%s'" % infile )
        logging.error( "\t'%s' %s" % (e.problem,e.problem_mark) )

    except Exception, e:
        logging.error( "There was a problem reading '%s', skipping" % infile )
        print e.message

    r = [ x for x in  dpath.util.search( data, "vars/name", yielded=True ) ]

    if len(r) > 1:
        logging.error( "Multiple names found in '%s', skipping" % infile )
        continue
    if len(r) == 0:
        logging.error( "No name found in '%s', skipping" % infile )
        continue

        
    # get name
    name = r[0][1]
    # process the name
    name = name.replace(" ","_")

    # generate filename
    dir = os.path.dirname( infile)
    ext = os.path.splitext( infile)[1]
    outfile = ''.join([name,ext])
    outfile = os.path.join( dir, outfile )

    if outfile == infile:
        logging.info("file does not need to be renamed, skipping")
        continue

    if os.path.isfile( outfile ):
        logging.error("output file appears to already exits (%s), skipping." % outfile )
        continue

    os.rename( infile, outfile )


