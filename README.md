# Learning Google ADK
Learning Agentic AI Development with Google ADK Step by Step.
This is my code repository, which I have created by following [Brandon Hancock's](https://www.youtube.com/@aiwithbrandon) [Agent Development Kit (ADK) Masterclass](https://www.youtube.com/watch?v=P4VFL9nIaIA&t=769s) on Youtube.. 

There are some changes that I have made from the code that Brandon has so graciously made available _for free_ on [his Github repo for the video](https://github.com/bhancockio/agent-development-kit-crash-course). For instance, I use `uv` for environment management instead of Python and `pip` as used by Brandon.

### How did I setup my environment
I am using [uv](https://docs.astral.sh/uv/), which is an extremely fast Python package & project manager. You should first install `uv` for your respective OS. Installation instructions can be found [here](https://docs.astral.sh/uv/getting-started/installation/). Once you have `uv` installed on your machine, follow the steps below:
1. Create a root folder to hold all the code for this video course (e.g. `~/home/learning_google_adk`). This can be created anywhere on your hard disk - I'll refer to this folder as `$CODE_ROOT` henceforth.
2. Open a terminal window (or command shell on Windows) and `cd $CODE_ROOT` folder.
3. Create a `requirements.txt` file with the entries [as shown here](./requirements.txt)
4. Create a local Python environment by running `uv init .` in the `$CODE_ROOT` folder.
5. Then run `uv pip install -r requirements.txt` from the `$CODE_ROOT` folder. This will install all the required packaged.

Once you have the environment ready, you should be able to follow Brandon's YouTube video and learn Google ADK.
