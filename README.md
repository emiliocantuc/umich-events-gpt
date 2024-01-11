# umich events gpt

Asking ChatGPT (gpt-3.5-turbo-1106) to go sift through the University of Michigan's events of the week and recommend which ones to attend.
Hosted [here](https://emiliocantuc.github.io/umich-events-gpt/).

- Events are downloaded from the [events API](https://events.umich.edu/week/json).
- Events with titles that contain a word in `blacklist.txt` are excluded.
- `prompt.txt` contains the part of the prompt that is customizable to different users (see `main.py` for the complete prompt).

## How to replicate
1. Fork this repo.
2. Enable Actions.
3. Go to the repo's settings > Actions > Workflow permissions and select `Read and write permissions`.
3. Set your OpenAI API key as a repository secret with name the `OPEN_AI_K`.
4. Set your events.umich.edu API link as a repository secret with the name `EVENTS_URL`. Here you can filter the types of events you want to consider. I've chosen, for example, `https://events.umich.edu/week/json?filter=types:21,5,13,19,18,&v=2`. **Make sure it is the JSON endpoint**.
