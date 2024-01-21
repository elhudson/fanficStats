import matplotlib.pyplot as plt
import numpy as np

plt.style.use("gruvbox.mplstyle")

def make_numerical(data):
    numeric = [
        "hits",
        "kudos",
        "bookmarks",
        "expected_chapters",
        "nchapters",
        "words",
        "comments",
    ]
    for n in numeric:
        data[n] = data[n].map(lambda x: 0 if x == "" else int(float(x)))


def make_graphs(data):
    targets = [
        d for d in data.dtypes.to_dict().keys() if data.dtypes[d] == np.dtype("int64")
    ]
    sets = []
    for t in targets:
        for v in targets:
            rel = set([t, v])
            if rel not in sets:
                plt.scatter(np.log(data[t]), np.log(data[v]))
                plt.xlabel(t)
                plt.ylabel(v)
                plt.xticks([])
                plt.yticks([])
                plt.savefig(f"./graphs/{t}_{v}")
                plt.show()
                sets.append(rel)


def make_log(fics, features):
    for feature in features:
        fics[feature + "_log"] = np.log2(fics[feature])
    fics.replace(to_replace=-np.inf, value=np.float64(-1), inplace=True)