# Author: Izaak Neutelings (May 2019)
###import os
###modulepath = os.path.dirname(__file__)

def hasBit(value,bit):
  """Check if i'th bit is set to 1, i.e. binary of 2^(i-1),
  from the right to the left, starting from position i=0."""
  # statusFlags: https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#GenPart
  # gen status flags stored bitwise, bits are:
  #    0 : isPrompt,                          8 : fromHardProcess,
  #    1 : isDecayedLeptonHadron,             9 : isHardProcessTauDecayProduct,
  #    2 : isTauDecayProduct,                10 : isDirectHardProcessTauDecayProduct,
  #    3 : isPromptTauDecayProduct,          11 : fromHardProcessBeforeFSR,
  #    4 : isDirectTauDecayProduct,          12 : isFirstCopy,
  #    5 : isDirectPromptTauDecayProduct,    13 : isLastCopy,
  #    6 : isDirectHadronDecayProduct,       14 : isLastCopyBeforeFSR
  #    7 : isHardProcess,
  ###return bin(value)[-bit-1]=='1'
  ###return format(value,'b').zfill(bit+1)[-bit-1]=='1'
  return (value & (1 << bit))>0
