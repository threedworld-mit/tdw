# Non-free models

In addition to the 200 or so free models in `models_core.json` and `models_special.json`, TDW has a non-free library of models: `models_full.json`, which contains an additional 2000 models. These models are near-photoreal and are tagged with semantic categories, just like the models of `models_core.json`. There are far more models and categories in `models_full.json` than `models_core.json`.

For the sake of convenience, the full library's [metadata file](../python/librarian/model_librarian.md) contains all of the records for `models_core.json`.

## How to access non-free models

### Requirements

- You must be affiliated with MIT, IBM, or Stanford. (This will change in the future.)
- Amazon S3 access keys

### How to obtain Amazon S3 access keys

If you haven't done so already, [email Jeremy Schwartz](mailto:jeremyes@mit.edu) to request access keys for the full model library. You will receive an email with the title “Welcome to ThreeDWorld(TDW)”. This email will contain login instructions and your username for the TDW Amazon AWS console, where you will generate your access credentials. _You will also receive a second email_, containing the temporary password associated with that username. Note this email will be an encrypted email, and will require entering an access key to open which will be sent to you separately via Slack DM. 

You must change your password immediately upon login, per the instructions below.  Also, you will not have permissions to perform any actions in the Console; you will only be able to generate your access credentials as described below.

After clicking on the link, you will be taken to the Amazon AWS Console page for the TDW account. Click on the down arrow marked in red below:

![](../images/models_full/screen1.jpg)

This will display the drop-down menu for your login. Click on “My Security Credentials”:

![](../images/models_full/screen2.jpg)

You will go to the credentials management page, where you will first change the temporary password you logged in with by clicking in the “Change password” button:

![](../images/models_full/screen3.jpg)

Next, you will generate your access key, which is in the form of a public / private key pair; click on the “Create access key” button as shown below. 

![](../images/models_full/screen3b.jpg)

This is your _only_ opportunity to save the information for both keys, so you must either download the CSV using the button highlighted below (recommended), or else show the secret access key and make a note of both keys.

![](../images/models_full/screen4.jpg)

### How to set up your credentials file

1. Create a new file here:

```
<home>/.aws/credentials
```

Where `<home>` is your home directory. Note that `credentials` doesn't have a file extension.

2. Add this to the file:

```
[tdw]
aws_access_key_id=<access key id>
aws_secret_access_key=<secret acccess key>
```

Replace `<access key id>` with your access key ID, and `<secret access key>` with your secret access key.

### How to validate your credentials and add a config file

You need a config file in addition to your credentials file:

```
<home>/.aws/config
```

You can create this config file in one of two ways.

#### 1. Copy-paste the following:

```
[default]
region = us-east-1
output = json
```

#### 2. Run TDW's own validation

With Python3:

```python
from tdw.tdw_utils import TDWUtils

TDWUtils.validate_amazon_s3()
```

This will validate that everything is set up correctly and generate a config file for you.

#### 3. (Optional) Create images of all of the models

You can run [`screenshotter.py --type models_full`](models_full.md) to generate images of every model in the library. Be aware that it will take at least an hour to create every image.