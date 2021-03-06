import simuvex
from itertools import count

fastpath_data_counter = count()

class receive(simuvex.SimProcedure):
    #pylint:disable=arguments-differ

    def run(self, fd, buf, count, rx_bytes):

        if self.state.mode == 'fastpath':
            # Special case for CFG generation
            if not self.state.se.symbolic(count):
                actual_size = count
                data = self.state.se.Unconstrained(
                    'receive_data_%d' % fastpath_data_counter.next(),
                    self.state.se.exactly_int(actual_size) * 8
                )
                self.state.memory.store(buf, data)
            else:
                actual_size = self.state.se.Unconstrained('receive_length', self.state.arch.bits)
            self.state.memory.store(rx_bytes, actual_size, endness='Iend_LE')

            return self.state.se.BVV(0, self.state.arch.bits)

        if ABSTRACT_MEMORY in self.state.options:
            actual_size = count
        else:
            actual_size = self.state.se.Unconstrained('receive_length', self.state.arch.bits)
            if CGC_NO_SYMBOLIC_RECEIVE_LENGTH in self.state.options:
                self.state.add_constraints(actual_size == min(self.state.se.max_int(count), self.state.memory._maximum_symbolic_size), action=True)
            else:
                self.state.add_constraints(self.state.se.ULE(actual_size, count), action=True)

        if self.state.satisfiable(extra_constraints=[count != 0]):
            data = self.state.posix.read(fd, count, dst_addr=buf)
            list(self.state.log.actions)[-1].size.ast = actual_size
            list(self.state.log.actions)[-2].data.ast = list(self.state.log.actions)[-1].actual_value.ast
            self.data = data
        else:
            self.data = None

        self.size = actual_size
        self.state.memory.store(rx_bytes, actual_size, condition=rx_bytes != 0, endness='Iend_LE')

        # TODO: receive failure
        return self.state.se.BVV(0, self.state.arch.bits)

from simuvex.s_options import ABSTRACT_MEMORY, CGC_NO_SYMBOLIC_RECEIVE_LENGTH
