import simuvex
import struct
import logging

l = logging.getLogger(name="procedures.libc_so_6.printf")

######################################
# _printf
######################################

class printf(simuvex.SimProcedure):
	def __init__(self):
		# This function returns
		# Add another exit to the retn_addr that is at the top of the stack now
		retn_addr = self.exit_return()
		l.debug("Got return address for %s: 0x%08x.", __file__, self._exits[0].concretize())