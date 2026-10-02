from core.state import state

def is_working():
    s = state()
    assert s.running is True # keyword assert ^-^

def working_without_crash():
    s = state()
    s.update(0.016)