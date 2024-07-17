import asyncio

GPT_MODEL = 'gpt-3.5-turbo'
system_prompt = "You are a helpful assistant."

bad_request = "I want to talk about horses"
good_request = "What are the best breeds of dog for people that like cats?"


async def get_chat_response(user_request):
    print("Getting LLM response")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request},
    ]
    response = {
        "choices": [
            {"message": {"content": "Here are some dog breeds that get along well with cats: Golden Retriever, Labrador Retriever, and Beagle."}}
        ]
    }
    print("Got LLM response")
    return response["choices"][0]["message"]["content"]

# Mock function 
async def topical_guardrail(user_request):
    print("Checking topical guardrail")
    messages = [
        {
            "role": "system",
            "content": "Your role is to assess whether the user question is allowed or not. The allowed topics are cats and dogs. If the topic is allowed, say 'allowed' otherwise say 'not_allowed'",
        },
        {"role": "user", "content": user_request},
    ]
    # Mock response
    if "cats" in user_request or "dogs" in user_request:
        response = {"choices": [{"message": {"content": "allowed"}}]}
    else:
        response = {"choices": [{"message": {"content": "not_allowed"}}]}
    print("Got guardrail response")
    return response["choices"][0]["message"]["content"]

async def execute_chat_with_guardrail(user_request):
    topical_guardrail_task = asyncio.create_task(topical_guardrail(user_request))
    chat_task = asyncio.create_task(get_chat_response(user_request))

    while True:
        done, _ = await asyncio.wait(
            [topical_guardrail_task, chat_task], return_when=asyncio.FIRST_COMPLETED
        )
        if topical_guardrail_task in done:
            guardrail_response = topical_guardrail_task.result()
            if guardrail_response == "not_allowed":
                chat_task.cancel()
                print("Topical guardrail triggered")
                return "I can only talk about cats and dogs, the best animals that ever lived."
            elif chat_task in done:
                chat_response = chat_task.result()
                return chat_response
        else:
            await asyncio.sleep(0.1) 


user_request = good_request  
response = asyncio.run(execute_chat_with_guardrail(user_request))
print(response)

user_request = bad_request 
response = asyncio.run(execute_chat_with_guardrail(user_request))
print(response)
