import subprocess, os

def run_list(args):
    p = subprocess.run(args, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode

def run_shell(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode

# Which python
print("python:", os.environ.get("VIRTUAL_ENV", "no venv"))
print("PATH:", os.environ.get("PATH","")[:500])

# Probe mingw git
print("\n=== mingw git probe ===")
out, err, rc = run_list(['/mingw64/bin/git', '--version'])
print(f"rc={rc} out={repr(out[:80])} err={repr(err[:80])}")

# Probe shell git
print("\n=== shell git probe ===")
out2, err2, rc2 = run_shell('git --version')
print(f"rc={rc2} out={repr(out2[:80])} err={repr(err2[:80])}")

# Probe git status with mingw
print("\n=== mingw git status ===")
out3, err3, rc3 = run_list(['/mingw64/bin/git', '-C', '/c/Users/hello/alforaijboard-gh', 'status', '--porcelain'])
print(f"rc={rc3} out={repr(out3[:100])} err={repr(err3[:100])}")

# Probe via bash -c
print("\n=== bash -c git status ===")
out4, err4, rc4 = run_list(['bash', '-c', 'git -C /c/Users/hello/alforaijboard-gh status --porcelain'])
print(f"rc={rc4} out={repr(out4[:100])} err={repr(err4[:100])}")
