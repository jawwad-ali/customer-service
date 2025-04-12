#  .venv\Scripts\activate
from supermen import triage_agent
from agents import Agent, trace, Runner, MessageOutputItem, ItemHelpers, HandoffOutputItem, ToolCallItem, ToolCallOutputItem
from model import AirlineAgentContext
import uuid
import asyncio
from connection import config

async def main():
    current_agent: Agent[AirlineAgentContext] = triage_agent
    input_items = []
    context = AirlineAgentContext()

    conversation_id = uuid.uuid4().hex[:16]

    while True:
        user_input = input('Enter your message?')
        with trace('Customer Service' , group_id = conversation_id):
            input_items.append({
                'role': 'user',
                'content': user_input
            })
            result = await Runner.run(current_agent , input_items , context = context, run_config=config)

            for new_item in result.new_items:
                agent_name = new_item.agent.name

                if isinstance(new_item , MessageOutputItem):
                    print(f'Agent Name {agent_name}: {ItemHelpers.text_message_output(new_item)}')

                elif isinstance(new_item, HandoffOutputItem):
                    print(f'Handed off output item from {new_item.source_agent.name} to {new_item.target_agent.name}')

                elif isinstance(new_item, ToolCallItem):
                    print(f'{agent_name} calling a tool.')

                elif isinstance(new_item, ToolCallOutputItem):
                    print(f'{agent_name} tool call output' , {new_item.output})

                else:
                    print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")

            input_items = result.to_input_list()
            current_agent = result.last_agent

if __name__ == "__main__":
    asyncio.run(main())


