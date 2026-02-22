"""Agent integration testing script for MedRBench environment."""

import json
import asyncio
import os

from openai import AsyncOpenAI
from openreward import AsyncOpenReward


async def main():
    """Test MedRBench environment with an agent on both diagnosis and treatment tasks."""
    or_client = AsyncOpenReward()
    oai_client = AsyncOpenAI()

    MODEL_NAME = "gpt-5.2"
    ENV_NAME = "YourOrg/medrb"
    SPLIT = "test"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        return

    environment = or_client.environments.get(name=ENV_NAME, base_url="http://localhost:8080")
    tasks = await environment.list_tasks(split=SPLIT)
    tools = await environment.list_tools(format="openai")

    print(f"Found {len(tasks)} tasks")

    # Test first diagnosis task and first treatment task
    diagnosis_tasks = [t for t in tasks if t.task_spec.get("task_type") == "diagnosis"]
    treatment_tasks = [t for t in tasks if t.task_spec.get("task_type") == "treatment"]

    test_tasks = [diagnosis_tasks[0], treatment_tasks[0]]

    for task in test_tasks:
        print(f"\n{'='*60}")
        print(f"Testing {task.task_spec['task_type']} task: {task.task_spec['case_id']}")
        print(f"{'='*60}\n")

        rollout = or_client.rollout.create(
            run_name=ENV_NAME.split("/")[-1] + "_test",
            rollout_name=f"test_{task.task_spec['task_type']}",
            environment=ENV_NAME,
            split=SPLIT,
            task_spec=task.task_spec
        )

        async with environment.session(task=task, secrets={"openai_api_key": OPENAI_API_KEY}) as session:
            prompt = await session.get_prompt()
            input_list = [{"role": "user", "content": prompt[0].text}]
            finished = False

            rollout.log_openai_response(message=input_list[0], is_finished=finished)

            while not finished:
                response = await oai_client.responses.create(
                    model=MODEL_NAME,
                    tools=tools,
                    input=input_list
                )

                rollout.log_openai_response(response.output[-1])
                input_list += response.output

                for item in response.output:
                    if item.type == "function_call":
                        tool_result = await session.call_tool(item.name, json.loads(str(item.arguments)))

                        reward = tool_result.reward
                        finished = tool_result.finished

                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": tool_result.blocks[0].text
                        })
                        rollout.log_openai_response(input_list[-1], reward=reward, is_finished=finished)

                        print(f"Tool: {item.name}")
                        print(f"Reward: {reward:.3f}")

                        if tool_result.finished:
                            finished = True
                            print('FINISHED!')
                            break


if __name__ == "__main__":
    asyncio.run(main())
