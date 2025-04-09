from langchain_ollama import ChatOllama
from tavily import TavilyClient
import operator
from dataclasses import dataclass, field
from typing_extensions import TypedDict, Annotated, Literal
import json
from langchain_core.runnables import RunnableLambda
from langgraph.graph import START, END, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage

tavily_search = TavilyClient(api_key="{your key}")
local_llm = "llama3.1"
llm = ChatOllama(model=local_llm, temperature=0.2)
llm_json_mode = ChatOllama(model=local_llm, temperature=0, format="json")


# from configuration import Configuration

## Query writer
query_writer_instructions = """Your goal is to generate targeted web search query.

The query will gather information related to specific topic. Heavily focused on extracting research/journal papers papers

Topic:
{research_topic}

Return your query as JSON object:
{{
    "query" : "string",
    "aspect" : "string",
    "rationale" : "string"
}}
"""

summarizer_instructions = """Your goal is to generate a high-quality summary of the web search results.

When EXTENDING an exisiting summary:
1. Seamlessly integrate new information without repeating what's already covered.
2. Maintain consistency with the exisiting content's style and depth
3. Only add new, non-redundant information
4. Ensure smooth transitions between existing and new content

When creating a NEW summary:
1. Highlight the most relevant information from each source
2. Provide a concise overview of the key points related to the report topic
3. Emphasize significant findings or insights
4. Ensure a coherent flow of information

In both cases:
- Focus on factual, objective information
- Maintain a consistent technical depth
- Avoid redundancy and repition
- DO NOT use phrases like "based on new results"  or "according ti the additional sources"
- DO NOT add a preamble like "Here is an extended summary ..." Just directly output the summary
- DO NOT add a Reference or Works Cited section
- MAKE SURE TO FOLLOW the structure of Summary in points and with references cited
"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.

Your tasks:
1. Identify knowledge gaps or areas that need deeper exploration
2. Generate a follow-up question that would help expand your understanding
3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered

Ensure the follow-up question is self-contained and includes necessary context for web search.

Return your analysis as JSON object:
{{
    "knowledge_gap": "string",
    "follow_up_query": "string"
}}
"""

@dataclass
class SummaryState():
  research_topic: str = None
  search_query: str = None
  web_search_results: Annotated[list, operator.add] = field(default_factory=list)
  sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
  research_loop_count: Annotated[int, operator.add] = 0
  running_summary: str = None

class SummaryStateInput(TypedDict):
  research_topic : str

class SummaryStateOutput(TypedDict):
  running_summary: str

def generate_query(state: SummaryState):
  print("Starting generation")
  prompt = query_writer_instructions.format(research_topic=state.research_topic)
  result = llm_json_mode.invoke([
      SystemMessage(content=prompt),
      HumanMessage(content="Generate a query for web search :")
  ])
  query = json.loads(result.content)
  return {"search_query": query["query"]}

def web_search(state: SummaryState):
  search_results = tavily_search.search(state.search_query, include_raw_content=True, max_results=1)["results"][0]
  return {
      "web_search_results": [search_results["content"]],
      "sources_gathered": [search_results["url"]],
      "research_loop_count": 1
  }
def summarize(state: SummaryState):
  messages = [SystemMessage(content=summarizer_instructions)]
  if state.running_summary:
    messages.append(HumanMessage(content=f"Existing summary:\n{state.running_summary}"))
    messages.append(HumanMessage(content=f"New Sources:\n{json.dumps(state.web_search_results, indent=2)}"))
  else:
    messages.append(HumanMessage(content=f"Sources:\n{json.dumps(state.web_search_results, indent=2)}"))
  result = llm.invoke(messages)
  return {"running_summary": result.content}

def reflect(state: SummaryState):
  prompt = reflection_instructions.format(research_topic=state.research_topic)
  result = llm_json_mode.invoke([
      SystemMessage(content=prompt),
      HumanMessage(content=state.running_summary)
  ])
  follow_up = json.loads(result.content)
  return {"search_query": follow_up["follow_up_query"]}

builder = StateGraph(SummaryState)

builder.add_node("generate_query", RunnableLambda(generate_query))
builder.add_node("web_search", RunnableLambda(web_search))
builder.add_node("summarize", RunnableLambda(summarize))
builder.add_node("reflect", RunnableLambda(reflect))

def rewrite(state: SummaryState) -> Literal["web_search", END]:
  if state.research_loop_count >= 3:
    return END
  else:
    return "web_search"

builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "web_search")
builder.add_edge("web_search", "summarize")
builder.add_edge("summarize", "reflect")
builder.add_conditional_edges("reflect", rewrite)

research_graph = builder.compile()

def inference(topic: str) -> str:
    initial_state: SummaryStateInput = {
        "research_topic" : topic
    }
    final_state: SummaryStateOutput = research_graph.invoke(initial_state)
    print("Final Summary:\n", final_state["running_summary"])
    return final_state["running_summary"]