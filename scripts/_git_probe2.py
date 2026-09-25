import subprocess

def run_list(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode

def run_shell(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode

print("=== run_list git status ===")
out, err, rc = run_list(['git', '-C', '/c/Users/hello/alforaijboard-gh', 'status', '--porcelain'])
print(f"rc={rc} out={repr(out[:100])} err={repr(err[:100])}")

print("=== run_shell git status ===")
out2, err2, rc2 = run_shell('git -C /c/Users/hello/alforaijboard-gh status --porcelain')
print(f"rc={rc2} out={repr(out2[:100])} err={repr(err2[:100])}")

print("=== run_list git rev-parse ===")
out3, err3, rc3 = run_list(['git', '-C', '/c/Users/hello/alforaijboard-gh', 'rev-parse', '--git-dir'])
print(f"rc={rc3} out={repr(out3)} err={repr(err3[:100])}")

print("=== run_shell git rev-parse ===")
out4, err4, rc4 = run_shell('git -C /c/Users/hello/alforaijboard-gh rev-parse --git-dir')
print(f"rc={rc4} out={repr(out4)} err={repr(err4[:100])}")
