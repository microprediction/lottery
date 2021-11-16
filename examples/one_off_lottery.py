from lottery.categoricallottery import CategoricalLottery
import itertools
from pprint import pprint

# This example shows how to mock a one-off lottery using conventions that are really designed for
# continuing lotteries. The

if __name__=='__main__':

    # Determine allowed values. These are str because the usual use is via JSON.
    # Let's suppose participants pick 3 numbers out of 6. A ticket looks like '1-5-6'
    allowed_values = [ '-'.join(c) for c in itertools.combinations(['1','2','3','4','5','6'],r=3) ]
    lottery = CategoricalLottery( allowed_values= allowed_values)

    # Bill and Mary buy tickets.
    # By default the lottery is opened for betting at a large negative time,
    # so the time at which they buy can be provided as zero, say.
    lottery.add(t=0, owner='bill', values=['1-3-4','1-2-5'], weights=None, amount = 1.0)
    lottery.add(t=0, owner='mary', values=['2-3-4','4-5-6','1-2-5'], weights=None, amount=1.0)

    lottery.close(t=1)   # This adds a 'fake' observation so that now bill and mary's predictions will
                         # valid for a ground truth revealed after t=1

    # Closing the lottery also prevents further bets from being counted. Sorry, Sally.
    lottery.add(t=2, owner='sally', values=['2-3-4', '4-5-6', '1-2-5'], weights=None, amount=1.0)

    # Some scenarios:
    pprint( lottery.payout( t=3, value='1-3-4' ) )
    pprint( lottery.payout( t=3, value='1-2-5' ) )
    pprint( lottery.payout( t=3, value='1-3-6' ) )
