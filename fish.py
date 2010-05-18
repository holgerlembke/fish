"""
    Swimming fishes progress indicator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Well, what can you say really? It's a swimming fish that animates when you
    call a certain function. Simple as that.

    How to use:

    .. code-block:: python

       import fish

       for datum_to_churn in data:
           fish.animate()
           churn_churn(datum_to_churn)
"""

import sys
import time
from itertools import cycle, count

ANSI_LINE_CLEAR = "\x1b[2K\r"

class SwimFishBase(object):
    def __init__(self, velocity=10, world_length=79, outfile=sys.stderr):
        self.worldstep = self.make_worldstepper()
        self.velocity = velocity
        self.world_length = world_length
        self.outfile = outfile
        self.last_hash = 0

    def animate(self, outfile=None, force=False):
        step = self.worldstep.next()
        # Refit the world so that we can move along an axis and not worry about
        # overflowing
        actual_length = self.world_length - self.own_length
        # As there are two directions we pretend the world is twice as large as
        # it really is, then handle the overflow
        pos = (self.velocity * step) % (actual_length * 2)
        reverse = pos < actual_length
        pos = int(round(abs(pos - actual_length), 0))
        fish = self.render(reverse=reverse)
        of = outfile or self.outfile
        curr_hash = force or hash((of, pos, fish))
        if force or curr_hash != self.last_hash:
            self.print_line(of, pos, fish)
            of.flush()
            self.last_hash = curr_hash

    def print_line(self, of, pos, fish):
        lead = " " * pos
        trail = " " * (self.world_length - self.own_length - pos)
        of.write(ANSI_LINE_CLEAR + lead + fish + trail + "\r")

class ProgressableFishBase(SwimFishBase):
    def __init__(self, *args, **kwds):
        total = kwds.pop("total", None)
        super(ProgressableFishBase, self).__init__(*args, **kwds)
        if total:
            # `pad` is the length required for the progress indicator,
            # It, at its longest, is `100% 123/123`
            pad = len(str(total)) * 2
            pad += 6
            self.world_length -= pad
        self.total = total

    def animate(self, *args, **kwds):
        prev_amount = getattr(self, "amount", None)
        self.amount = kwds.pop("amount", None)
        if self.amount != prev_amount:
            kwds["force"] = True
        return super(ProgressableFishBase, self).animate(*args, **kwds)

    def print_line(self, of, pos, fish):
        if not self.amount:
            return super(ProgressableFishBase, self).print_line(of, pos, fish)

        # Get the progress text
        if self.total:
            part = self.amount / float(self.total)
            done_text = str(self.amount).rjust(len(str(self.total)))
            progress = "%3.d%% %s/%d" % (part * 100, done_text, self.total)
        else:
            progress = str(amount)

        lead = " " * pos
        trail = " " * (self.world_length - self.own_length - pos)
        of.write(ANSI_LINE_CLEAR + lead + fish + trail + progress + "\r")

class BassLook(SwimFishBase):
    def render(self, reverse=False):
        return "<'((<" if reverse else ">))'>"

    own_length = len(">))'>")

class SalmonLook(SwimFishBase):
    def render(self, reverse=False):
        return "<*}}}><" if reverse else "><{{{*>"

    own_length = len("><{{{*>")

class SwimFishNoSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return count()

class SwimFishTimeSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return iter(time.time, None)

class Fish(ProgressableFishBase, SwimFishTimeSync, BassLook):
    """The default swimming fish, the one you very likely want to use.
    See module-level documentation.
    """

default_fish = Fish()
animate = default_fish.animate

if __name__ == "__main__":
    try:
        total = int(sys.argv[1])
        f = Fish(total=total)
        for i in range(total):
            f.animate(amount=i+1)
            time.sleep(0.1)
    except IndexError: 
        while True:
            animate()
            time.sleep(0.1)
    
