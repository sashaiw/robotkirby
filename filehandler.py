import os


def write(server,f,s):
    filepath = f"db/{server}/{f}.txt"
    print(filepath)

    if not os.path.exists("db/" + server):
        os.makedirs("db/" + server)

    if not os.path.exists(filepath):
        open(filepath, "a").close()

    f = open(filepath)
    fa = [item.rstrip("\n") for item in f.readlines()]
    if s not in fa:
        f = open(filepath, "a")
        f.write(s + "\n")
        f = open(filepath)
        fa = [item.rstrip("\n") for item in f.readlines()]
        return fa
    else:
        return False


def remove(server,f,s):
    filepath = f"db/{server}/{f}.txt"

    if os.path.exists(filepath):
        f = open(filepath)
        fa = [item.rstrip("\n") for item in f.readlines()]
        if s in fa:
            f = open(filepath,"w")
            for line in fa:
                if line != s:
                    f.write(line + "\n")
                    print(line)

        f = open(filepath)
        fa = [item.rstrip("\n") for item in f.readlines()]
        return fa
    else:
        return False


def read(server, f):
    filepath = f"db/{server}/{f}.txt"

    if os.path.exists(filepath):
        f = open(filepath)
        fa = [item.rstrip("\n") for item in f.readlines()]
        if len(fa) > 0:
            return fa
        else:
            return False
    else:
        return False


def kill(server, f):
    filepath = f"db/{server}/{f}.txt"

    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    else:
        return False
