from benchmarker import Benchmarker

"""
Objects data benchmarks.
"""

if __name__ == "__main__":
    b = Benchmarker()

    header = "| Test | FPS |\n| --- | --- |\n"
    output = header[:]

    rows = []

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img",
                      row="--boxes --images --passes _img"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_id",
                      row="--boxes --images --passes _id"))

    b.start()
    rows.append(b.run(boxes=True,  images=True, passes="none", id_grayscale=True,
                      row="--boxes --id_grayscale --images --passes none"))

    b.start()
    rows.append(b.run(boxes=True, id_colors=True, images=True, passes="none",
                      row="--boxes --id_colors --images --passes none"))

    b.start()
    rows.append(b.run(boxes=True, transforms=True,
                      row="--boxes --transforms"))
    for row in rows:
        output += row + "\n"
    print(output)

    b.communicate({"$type": "terminate"})
