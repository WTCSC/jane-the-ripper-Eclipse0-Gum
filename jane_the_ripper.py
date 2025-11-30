import hashlib
from pathlib import Path
import argparse

def load_hashes(path: Path):
    if not path.exists(): 
        raise FileNotFoundError(path)
    return {line.strip().lower() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}

def crack(hashes_file: Path, wordlist_file: Path, algo="md5", encoding="latin-1"):
    targets = load_hashes(hashes_file)
    if not targets:
        return {}
    h = hashlib.new(algo)  
    digest_len = h.digest_size * 2

    
    targets = {t for t in targets if len(t) == digest_len}
    cracked = {}

    with wordlist_file.open(encoding=encoding, errors="replace") as f:
        for i, raw in enumerate(f, 1):
            pw = raw.rstrip("\n")
            if not pw or pw.startswith("#"):
                continue
            d = hashlib.new(algo, pw.encode(encoding)).hexdigest().lower()
            if d in targets:
                print(f"[+] {d} -> {pw}")
                cracked[d] = pw
                targets.remove(d)
                if not targets:
                    break
            if i % 50000 == 0:
                print(f"Processed {i} lines; {len(targets)} remaining")
    if targets:
        print(f"[!] {len(targets)} not found")
    return cracked 

def main():
    p = argparse.ArgumentParser()
    p.add_argument("hashes", nargs="?", default="hashes.txt")
    p.add_argument("wordlist", nargs="?", default="wordlist.txt")
    p.add_argument("--algo", default="md5")
    args = p.parse_args()
    try:
        result = crack(Path(args.hashes), Path(args.wordlist), algo=args.algo)
    except FileNotFoundError as e:
        print("File missing:", e)
        return 2
    print(f"Cracked {len(result)} entries")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
