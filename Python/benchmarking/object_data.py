from benchmarker import Benchmarker

"""
Objects data benchmarks.
"""

if __name__ == "__main__":
    b = Benchmarker()

    output = "| Test | FPS |\n| --- | --- |\n"

    rows = []

    b.start()
    rows.append(b.run(boxes=True, transforms=True,
                      row="--boxes --transforms"))

    b.start()
    rows.append(b.run(boxes=True, rigidbodies=True,
                      row="--boxes --rigidbodies"))

    b.start()
    rows.append(b.run(boxes=True, collisions=True,
                      row="--boxes --collisions"))

    b.start()
    rows.append(b.run(boxes=True, bounds=True,
                      row="--boxes --bounds"))

    b.start()
    rows.append(b.run(boxes=True, transforms=True, rigidbodies=True, collisions=True, bounds=True,
                      row="--boxes --transforms --rigidbodies --collisions --bounds"))

    for row in rows:
        output += row + "\n"
    print(output)

    b.communicate({"$type": "terminate"})
