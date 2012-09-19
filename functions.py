from subprocess import Popen, PIPE

def execute(command, error_message, capture_output=False):
    """Run command on command-line"""
    stdout = PIPE if capture_output else None
    
    print command
    p = Popen(command, shell=True, stdout=stdout)    
    (out,err) = p.communicate()
    
    if p.returncode != 0:
        raise SystemExit('\nERROR: %s' % error_message)
    
    return out
