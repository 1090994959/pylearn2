__authors__ = "Ian Goodfellow"
__copyright__ = "Copyright 2010-2012, Universite de Montreal"
__credits__ = ["Ian Goodfellow"]
__license__ = "3-clause BSD"
__maintainer__ = "Ian Goodfellow"
__email__ = "goodfeli@iro"

from theano.compile import Mode
import theano
from pylearn2.utils import hex_digest

class Record(Mode):
    """
    Records all computations done with a function in a file at output_path
    Prints the index of each apply node and md5 digests of the numpy ndarrays
    it receives as inputs and produces as outputs.
    """
    def __init__(self, path, replay=False):

        if replay:
            f = open(path, 'r')
        else:
            f = open(path, 'w')

        known_fgraphs = set([])

        def handle_line(line, i, node, fn):
            assert line.endswith('\n')
            if replay:
                old_line = f.readline()
                if old_line != line:
                    print 'Replay detected mismatch'
                    print 'I wanted to write:'
                    if len(line) > 100:
                        print line[0:100]+'...'
                    else:
                        print line
                    print 'when previous job wrote:'
                    if len(old_line) > 100:
                        print old_line[0:100]+'...'
                    else:
                        print old_line
                    print 'while processing node i='+str(i)+':'
                    print 'str(node):',str(node)
                    print 'Symbolic inputs: '
                    for elem in node.inputs:
                        print theano.printing.min_informative_str(elem)
                    print 'str(output) of outputs: '
                    for elem in fn.outputs:
                        assert isinstance(elem, list)
                        elem, = elem
                        print str(elem)
                    print '__repr__ of outputs: '
                    for elem in fn.outputs:
                        print elem[0].__repr__()
                    print 'function name: '+node.fgraph.name
                    raise AssertionError("Non-determinism detected.")
            else:
                f.write(line)

        def callback(i, node, fn):
            fgraph = node.fgraph
            assert fgraph.name is not None
            if fgraph not in known_fgraphs:
                assert not any([elem.name == fgraph.name for elem in known_fgraphs])
                known_fgraphs.add(fgraph)
                num_app = len(fgraph.apply_nodes)
                line = 'Function '+fgraph.name+' has '+str(num_app)+' apply nodes.\n'
                handle_line(line, i, node, fn)

            line = 'Function name: '+str(fgraph.name) + '\n'
            handle_line(line, i, node, fn)
            line = 'Node '+str(i)+':'+str(node)+'\n'
            handle_line(line, i, node, fn)
            assert all([isinstance(x, list) and len(x) == 1 for x in fn.inputs])
            def digest(x):
                x = x[0]
                return hex_digest(x)
            inputs_digest = ' '.join([digest(x) for x in fn.inputs])
            line = 'Inputs: ' + inputs_digest + '\n'
            handle_line(line, i, node, fn)
            fn()
            outputs_digest = ' '.join([digest(x) for x in fn.outputs])
            line = 'Outputs: ' + outputs_digest + '\n'
            handle_line(line, i, node, fn)

        wrap_linker = theano.gof.WrapLinkerMany([theano.gof.OpWiseCLinker()], [callback])
        super(Record, self).__init__(wrap_linker, optimizer='fast_run')
