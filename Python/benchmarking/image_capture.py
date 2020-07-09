from argparse import ArgumentParser
from benchmark_utils import PATH
from benchmarker import Benchmarker
from platform import system


"""
Image capture benchmarks
"""


def granular():
    output = "| Test | FPS |\n| --- | --- |\n"

    rows = []

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img",
                      row="--images --passes _img"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_id",
                      row="--boxes --images --passes _id"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img", hi_res=True,
                      row="--images --passes _img --hi_res"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img", png=True,
                      row="--images --passes _img --png"))

    b.start()
    b.run(boxes=True, images=True, passes="_img_id",
          row="--boxes --images --passes _img_id")

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img", hi_res=True, size=1024,
                      row="--images --passes _img --hi_res --size 1024"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_id", hi_res=True, size=1024,
                      row="--images --passes _id --hi_res --size 1024"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img_id", hi_res=True, size=1024,
                      row="--images --passes _img_id --hi_res --size 1024"))

    b.start()
    rows.append(b.run(boxes=True, images=True, passes="_img_id", hi_res=True, size=1024, png=True,
                      row="--images --passes _img_id --hi_res --size 1024 --png"))

    for row in rows:
        output += row + "\n"
    print(output)


def write_to_main():

    b.start()
    tr = b.run(boxes=True, transforms=True, return_row=False)

    b.start()
    lo = b.run(images=True, passes="_img", return_row=False)
    b.start()
    hi = b.run(images=True, passes="_img", return_row=False, hi_res=True, size=1024)

    txt = PATH.read_text()
    txt = txt.replace("$TRANSFORMS_" + machine_key, str(tr))
    txt = txt.replace("$IMG_LOW_" + machine_key, str(lo))
    txt = txt.replace("$IMG_HIGH_" + machine_key, str(hi))
    PATH.write_text(txt)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--main', action='store_true')
    parser.add_argument('--machine', type=str, default='legion_lenovo', choices=['legion_lenovo', 'braintree', 'node11'])
    args = parser.parse_args()

    machine_key = args.machine.upper()
    if machine_key == "LEGION_LENOVO":
        if system() == "Windows":
            machine_key += "_WINDOWS"
        else:
            machine_key += "_UBUNTU"

    b = Benchmarker()

    if args.main:
        write_to_main()
    else:
        granular()
    b.communicate({"$type": "terminate"})
