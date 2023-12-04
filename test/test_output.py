import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'src'))

#print(sys.path)

from optimization import test

def test_run_output():
    result = 1
    assert result == 2
