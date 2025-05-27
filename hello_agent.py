import openai

assistant_id = "asst_ZPD18W6Okw278Fwu7U4MmWAP"

client = openai.OpenAI()

thread = openai.beta.threads.create()

while True:
    # Get user input
    user_input = input("\nYou (or press Enter to stop): ").strip()
    if not user_input:
        break

    # Add the user's message to the thread
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    # Create a run with streaming enabled
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        stream=True
    )

    for event in run:
        if event.event == "thread.run.failed":
            err = event.data.last_error
            print(f"[ERROR] {err.code}: {err.message}")
        elif event.event == "thread.message.delta":
            delta = event.data.delta
            if delta and delta.content:
                # content is a list of chunks; each .text.value has the string
                print(delta.content[0].text.value, end="", flush=True)
        elif event.event == "thread.run.step.delta":
            delta = event.data.delta
            # this is function calling, need to actually call it
        else:
            print(f"[DEBUG] event.event → {event.event!r}")

    print()  # newline after streaming
