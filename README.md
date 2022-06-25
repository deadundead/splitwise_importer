# splitwise_importer
A simple TUI utility to upload your bank account log to Splitwise, written in `Python` (tested with 3.7.1)

Splitwise_importer works with CSV files exported from your bank App or website.
Currently you must also specify a Splitwise group. All expenses would be created in this group, and split equally between all members of the group.

The script was created out of frustration at manually creating Splitwise expenses for the family budget for a whole month.

DISCLAIMER: 
This is not an official API. All the trademarks and copyright belongs to Splitwise.com.

# Installation
Clone the repository with submodules:

```git clone --recurse-submodules https://github.com/deadundead/splitwise_importer```

# Dependencies
splitwise_importer depends on the following packages installable via pip:
- [`Pandas`](https://pandas.pydata.org/docs/getting_started/install.html)
- [`PyYaml`](https://pypi.org/project/PyYAML/)
- [`requests-oauthlib`](https://pypi.org/project/requests-oauthlib/)

Some packages are included as git submodules due to current PyPI versions missing various fixes:
- [`Splitwise`](https://github.com/namaggarwal/splitwise)
- [`npyscreen`](https://github.com/npcole/npyscreen)

# How to use
## Preparing config files
splitwise_importer works with two main config files:
- `config.yaml`
- `mccDic.yaml`

To prepare the configuration files, you must:
- Open `example_config.yaml` file in text editor.
- [Get](https://secure.splitwise.com/apps) the API key, consumer ID and consumer Secret from Splitwise.
- Download your bank account log in `CSV` format for the dates of interest. See the layout (which column corresponds to which data).
- Copy `group_id` from the link to your group `https://secure.splitwise.com/#/groups/<group_id>`.
- Fill the `example_config.yaml` file with auth and layout data. Save it as `config.yaml`.
- In the `mccDic.yaml` file specify the correspondence between your bank payment types and Splitwise categories.
e.g. `Grocery store : Groceries`. The whole list of categories is given in the file. If you don't care, just create a dummy entry e.g. `Dummy : General`. All unspecified catagories will be set as 'General' expenses.

After this you are hopefully set up and ready to go!

## Using splitwise importer
Download your bank log CSV file.
Open your console terminal and run:

```python3 <path_to_splitwise_importer>/importer.py```

or create an alias.

The file selection dialogue will open. 

Navigate with arrow keys or mouse (press `Enter` to open folders and select file), select the bank log CSV file and confirm the selection.

Scroll through the list of your operations with arrow keys, and select them with spacebar (a yellow cross will appear to the left of selected operations).

Then select OK and press `Enter`. 

If auth data is correct, the program will output OK status or any errors for sending each entry to the Splitwise.

