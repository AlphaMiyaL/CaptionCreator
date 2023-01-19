import openai


class OpenAi:
    def __init__(self):
        # Initialize the openai API key
        openai.api_key = "OPENAI_API_KEY"

    def caption(self, labels):
        # Build the prompt for GPT-3
        prompt = f"Caption for an image with labels: {', '.join(label['Name'] for label in labels['Labels'])}"

        # Generate a caption using GPT-3
        response = openai.Completion.create(engine="text-davinci-002", prompt=prompt)

        # Extract the generated caption
        caption = response["choices"][0]["text"]

        print(caption)