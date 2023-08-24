from os.path import join
from os import getcwd
import clr
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


"""
This script is not a controller. It is an example of how to use Clatter without TDW.

To run this script, install pythonnet: pip install pythonnet.

This folder contains the Clatter.Core.dll library. If you want to write a script based off of this one, you must copy Clatter.Core.dll as well.

On Windows, you may need to unblock the dll: Right-click the file, select Properties, click "Unblock", and press OK.
"""

clr.AddReference(join(getcwd(), "Clatter.Core.dll"))
from System import Random
from Clatter.Core import ImpactMaterial, ScrapeMaterial, ImpactMaterialData, ScrapeMaterialData, ClatterObjectData, Scrape, WavWriter

# Load the materials.
primaryMaterial = ImpactMaterial.glass_1
secondaryMaterial = ImpactMaterial.stone_4
scrapeMaterial = ScrapeMaterial.ceramic
ImpactMaterialData.Load(primaryMaterial)
ImpactMaterialData.Load(secondaryMaterial)
ScrapeMaterialData.Load(scrapeMaterial)

# Set the objects.
primary = ClatterObjectData(0, primaryMaterial, 0.2, 0.2, 1)
secondary = ClatterObjectData(1, secondaryMaterial, 0.5, 0.1, 100, scrapeMaterial)

# Initialize the scrape.
scrape = Scrape(scrapeMaterial, primary, secondary, Random())

# Define the output path.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("scrape_no_controller")
if not path.exists():
    path.mkdir(parents=True)
path = path.joinpath("scrape.wav")
print(f"Audio will be saved to: {path}")

# Start writing audio.
writer = WavWriter(str(path.resolve()), True)

# Define the acceleration.
a = 0.05
# Get the number of chunks per scrape.
num_events = Scrape.GetNumScrapeEvents(a)
# Define speeds.
speeds = [0, 2, 0.5, 3, 0.5]

# Generate audio.
for i in range(len(speeds) - 1):
    if speeds[i + 1] > speeds[i]:
        dv1 = speeds[i + 1] - speeds[i]
        increase = True
    else:
        dv1 = speeds[i] - speeds[i + 1]
        increase = False
    dv = 0
    while dv < dv1:
        # Accelerate.
        dv += 0.05
        v = speeds[i] + (dv if increase else -dv)
        # Generate audio.
        scrape.GetAudio(v)
        # Write to the save file.
        writer.Write(scrape.samples.ToInt16Bytes())
# Stop writing.
writer.End()
