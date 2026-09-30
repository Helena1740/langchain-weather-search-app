#============SETUP================================================
Download Anaconda and run Anaconda prompt
run -> where conda
then in PowerShell (VSCode) -> & (command mode) "URL from previous step" init powershell 
and reopen PowerShell
If something goes wrong, then we try to put -> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned and start a new terminal


& - as powershell treats everything in quotes as a string, and even may return the same string


Then:
conda create -n langagent python=3.11 -y

conda activate langagent

python -m pip install -r requirements.txt -> more accurate with python -m due to environments


#===========VIRTUAL ENVIRONMENT SETUP==============================
How to make sure that we are in the virtual environment?
where.exe python or Get-Command python -> to check where is the pythin with source, where anaconda\envs\langagent\python.exe
conda list langchain -> check packages in active environment
conda list -n langagent langchain -> checks packages in specific environment without activating it
python -m pip show langchain -> checks in which environment is the package langchain 


#==========GIT INSTALLATION========================================

Git Installation

Option 1:
The cleanest way of creating new project is cloning from GitHub
- Create a repository in GitHub and add README.md file
- Copy URL
- Go to the parent folder for the project
- git clone <URL>.git
- cd <project-folder>
- code .
- Create snapshot after uploading all files: git add . -> git commit -m "Setup complete & files uploaded" -> git push

Option 2:
We already have a folder, then we go to the github and create repository without anything (readme file, .gitignore, licence)
Go inside our local project folder
git init -> to create a hidden folder .git, where the history will be stored
Create .gitignore file where we put:
.env
__pycache__/
*.pyc
.ipynb_checkpoints/
.vscode/
Make the first commit: git add . -> git status (check if there is no .env file) -> git commit -m "Initial commit"
Then, we connect to github:
git branch -M main -> our current branch is main
git remote add origin <github URL>.git -> origin is the nickname for the github repository and URL is the remote repo in github, tells our local git that the project
is connected to the github repo
git push -u origin main -> u is to remember the connection so that later we can just use git push, main is our local branch  

or we just use through:
Source Control Panel (Ctrl + Shift + G) + .gitignore

Typical workflow:
edit -> add -> commit -> push (git status -> git add . -> git commit -m "message" -> git push)

main is the stable version of the project
git switch -c feature/recommendation-model -> a new branch to test out new feature in new folder called feature <-> we can use git checkout -b -> but it's an older version
git switch main
git pull
git switch -c ....
git status -> git add -> git commit -> git push -u origin <new-feature branch>

git push -u origin feature/recommendation-model -> when we work with local feature/branch and push into remote repo origin, and it creates a new branch remotely -> after using -u, later we can use git push while we are on the same branch
'set upstream' -> opposite direction usually


Usually, after push there is a Pull Request -> code review -> CI/tests -> approval -> merge to main

Then, if everything is ok, we merge it with the main branch

Commands:
git status -> check the current status, what's happening, use it all the time
git diff -> what exactly have I changed? -> very useful before committing
git log -> what happened in the past, history
git log --oneline -> more convenient version
git fetch -> check what's on github without changing my files, just what changes there are to inspect what happened
git pull -> get the remote changes into my local branch
git branch -> what branches exist or to check local branch
git remote -v -> to check the connection between remote and local 
git remote add origin <GitHub URL> -> to connect remote and local
git branch new-feature -> just creates new-feature branch but doesn't switch to it
git merge -> combine branches -> git switch main -> git merge feature/recommendation-systems
git stash -> temporarily puts aside unfinished changes if we don't want to commit unfinished code (git stash -> git switch bug-fix git switch feature-work (continue work) -> git stash pop -> unfinished changes come back)
git rebase -> it can move our currect feature work to the latest main branch = replay the work on top of the latest main) -> more advanced, be careful
git reset -> move my branch/history backward, pointer points to the previous branch, git reset --soft/mixed/hard, better not to use --hard casually
git revert <commit> -> undo a commit safely, it just creates a new commit that undoes an old commit instead of deleting a history. This is generally safer for shared branches like main



#==========================PROJECT START========================================
- Create files and folder structure
- For .ipynb file we need to select langagent kernel/environment and install libraries
- Write whole code
- We convert this notebook .ipynb into an application file app.py as we need .py file in production
- We may first put all final code into main.py and add new final-prod-ready version with streamlit UI in app.py, asking ChatGPT to create a UI
- In Windows, we may need to put code certifi and os.environ["SSL_CERT_FILE"] = cerfiti.where() to resolve potential path issues
- .gitignore add all .env in all folders, put all API_KEYS into all .env files
- streamlit run app.py, don't forget to install as package
- To render, we may use render.com website but before we upload all code into GitHub
- Don't forget each time run and choose kernel or environment, where the code will run
- Check for potential quotation marks conflicts, depreciated functions, add docstring as a description for custom functions as tools
- Good practice: check tools independently before building the agent
- Agent = the brain + instructions for decision-making, AgentExecutor = the thing that actually runs the process (depreciated), current LC's create_agent already represents this agent loop as a graph, so newer API removes the separation
- Whole workflow: IMPORTS (bring libraries into Python) -> API KEYS (authenticate with services) -> TOOLS (give the agent the abilities) -> LLM (give the agent a 
brain) -> PROMPT (give it behavioral instructions) -> AGENT (connect brain + tools + instructions) -> EXECUTION (give it a task)
- LLM + tools + agent loop
- Temperature may differ based on the task: 0-0.2 -> for tool calling, extraction. classification; creative ideas -> 0.8-1.2+, normal business assistant -> 0.2-0.5 but now rather than knobbing temperature we knob which model to use and its reasoning effort
- If we use external prompt, we also need to make sure its safe by trying out several different prompts, testing and evaluating, sometimes, we need to manually write a prompt for our specific task
- Agent quality depends not only on the system prompt but also tool description as a part of a prompt
- Good predefined prompts: 1. model provider documentation (OpenAI, Gemini, etc.), 2. LangChain/LangSmith examples (agent patterns and templates), 3. our own prompt library (prompts that OUR application has tested -> eventually becomes the most important in production)
- "messages" in agent invocation is a part of bigger dictionary -> other may be: "user_preferences", "current_city", etc. All are fields in agent state, represents state schema, fields match what the agent/state expects
- When the user gets an answer after agent.invoke, the history of messages will stay and without persistence/checkpointing, another completely separate agent.invoke(), the previous conversation isn't automatically remembered; with a checkpointer + thread, the message history can persist between calls. Each .invoke() is a new run, to save a history, we may manually add to our next invoke apart from our request in "messages" or use checkpointing/persistence
- Maximum length of history memory depends on the context window (tokens) -> trim/delete previous or summarize (# each 4000 tokens or save the latest 20 messages) or filter (choose only necessary or delete unnecessary tools' history)
- Upload to the GitHub with .gitignore file -> render.com -> New -> Web Service -> Name, Public Git Repository -> GitHub URL
- Always make sure you are at the correct virtual environment
