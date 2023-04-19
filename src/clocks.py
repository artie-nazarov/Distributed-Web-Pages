def increment(clock, id):
    """Increment the clock at index id"""
    extend_clock_len(clock, id+1)
    clock[id] += 1

def new_clock(size):
    """Create and return a clock of size size"""
    return [0] * size

def extend_clock_len(clock, new_len):
    """Takes a clock and extends it to the length of new_len, assumes new_len is greater than current length"""
    clock.extend([0]* (new_len - len(clock)))

def equalize_clock_len(clock1, clock2):
    """Takes two clocks and ensures they have the same len"""
    if len(clock1) > len(clock2):
        extend_clock_len(clock2, len(clock1))
    elif len(clock1) < len(clock2):
        extend_clock_len(clock1, len(clock2))

def combine_clocks(clock1, clock2):
    """Takes two clocks, and updates clock1 to the most updated value"""
    #ensure equal length
    equalize_clock_len(clock1, clock2)
    for i in range(len(clock1)):
        clock1[i] = max(clock1[i], clock2[i])

def compare_clocks(clock1, clock2):
    """
    Takes two clocks and returns info on if they're concurrent

    Returns -1 if clock1 is in the past of clock2, 
             0 if clock1 is concurrent with clock2,
             1 if clock1 is in the future of clock2
             2 if clock1 is equal to clock2
    """
    #track if greater/lesser value is found
    found_greater = False
    found_lower = False

    #loop through the values in each clock and compare them
    for i1, i2 in zip(clock1, clock2):
        if i1 < i2:
            found_lower = True
        if i1 > i2: 
            found_greater = True
    
    #if both found, clock1 is concurrent 
    #if one found, clock1 is past/future
    #if none found, the clocks are equal
    if found_lower and found_greater:
        return 0
    elif found_lower:
        return -1
    elif found_greater:
        return 1
    else:
        return 2

