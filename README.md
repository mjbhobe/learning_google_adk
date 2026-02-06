# Learning Google ADK
Learning Agentic AI Development with Google ADK Step by Step.

This is my code repository, which I have created by following [Brandon Hancock's](https://www.youtube.com/@aiwithbrandon) [Agent Development Kit (ADK) Masterclass](https://www.youtube.com/watch?v=P4VFL9nIaIA&t=769s) on Youtube.. 

There are some changes that I have made from the code that Brandon has so graciously made available _for free_ on [his Github repo for the video](https://github.com/bhancockio/agent-development-kit-crash-course). For instance, I use `uv` for environment management instead of Python and `pip` as used by Brandon.

### How did I setup my environment
I am using [uv](https://docs.astral.sh/uv/), which is an extremely fast Python package & project manager. You should first install `uv` for your respective OS. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/). Once you have `uv` installed on your machine, follow the steps below:
1. Create a root folder to hold all the code for this video course (e.g. `~/home/learning_google_adk`). This can be created anywhere on your hard disk - I'll refer to this folder as `$CODE_ROOT` henceforth.
2. Open a terminal window (or command shell on Windows) and `cd $CODE_ROOT` folder.
3. Created a `requirements.txt` file with the entries [as shown here](./requirements.txt)
4. Created a local Python environment by running `uv init . [--python 3.12]` in the `$CODE_ROOT` folder. The `--python 3.12` is optional and used to specify a specific Python version to use. If omitted, it will default to latest Python version available.
5. Activated the just created environment by running (on Windows: `.venv\Script\activate.bat`; on Linux/Mac: `source .venv/bin/activate`). You should see your command prompt change to reflect the new Python environment is in use.
5. Then run `uv pip install -r requirements.txt` or `uv add -r requirements.txt` from the `$CODE_ROOT` folder. This will install all the required packaged.

### When you are cloding this Github Repo
Firstly, fell free to do so. I am sharing code for learning purpose only with no fit-for-purpose guarantees!

You should first install `uv` for your respective OS. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/). Once you have `uv` installed on your machine, follow the steps below.

Assume you are cloning this repo to `c:\code` folder on Windows or `~/code` folder on Linux or a Mac. The `git clone ...` command will create a `~/code/learning_google_adk` subfolder (on Linux/Mac) or a `c:\code\learning_google_adk` (on a Windows machine)

**Part A: setting up your local Python Environment**

1. `cd ~/code/learning_google_adk` or `cd c:\code\learning_google_adk` folder.
2. Run `uv venv` to initialize a Python environment in the above folder. This command will create a `.venv` sub-folder.
3. Activate the new environment just created:
* On Windows, run `.venv\Scripts\activate.bat`
* On Linux/Max, run `source .venv\bin\activate`
* This will activate the new environment and your command prompt will change to reflect the new Python environment is in use. You could see something like:
`(learning_google_adk) $> `
4. Run `uv pip install --editable .`. This command will read the `pyproject.toml` file and install all the required modules from it. This will setup your environment from a GitHub clone.

**NOTE:** Repeat steps 3 & 4 everytime you `pull` from the Github repo.

**Part B: setting up API key for use with Google's Gemini models**

<< TODO >>

Once you have the environment ready, you should be able to follow Brandon's YouTube video and learn Google ADK.
