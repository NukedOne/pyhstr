import collections


class Writer:
    def write(self, path, thing):
        with open(path, "w") as f:
            for thingy in thing:
                print(thingy, file=f)


class Reader:
    def read(self, path):
        history = []
        with open(path, "r") as f:
            for command in f:
                history.append(command.strip())
        return [
            x[0] for x in sorted(
                collections.Counter(history).items(), key=lambda y: -y[1]
            )
        ]
