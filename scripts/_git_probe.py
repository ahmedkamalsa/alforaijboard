import subprocess
def get(*args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.stdout.strip(), p.stderr.strip(), p.returncode

out, err, rc = get('git', '-C', '/c/Users/hello/alforaijboard-gh', 'rev-parse', '--git-dir')
print('rev-parse:', repr(out), 'rc:', rc)
out2, err2, rc2 = get('git', '-C', '/c/Users/hello/alforaijboard-gh', 'status', '--porcelain')
print('status rc:', rc2, 'out len:', len(out2), 'err:', repr(err2[:200]))
