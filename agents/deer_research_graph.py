import operator
from typing import Annotated, List, TypedDict, Union

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from loguru import logger

class ResearchState(TypedDict):
    # The list of messages in the conversation
    messages: Annotated[List[BaseMessage], operator.add]
    # The current research query
    query: str
    # Gathered data from researchers
    research_results: List[str]
    # Analysis from the analyst agent
    analysis: str
    # Current agent node
    next_step: str

def supervisor_node(state: ResearchState):
    logger.info("Supervisor: Orchestrating research flow.")
    # Logic to decide whether to research, analyze, or end
    if not state.get("query"):
        return {"next_step": "END"}
    if not state.get("research_results"):
        return {"next_step": "researcher"}
    if not state.get("analysis"):
        return {"next_step": "analyst"}
    return {"next_step": "END"}

def researcher_node(state: ResearchState):
    logger.info(f"Researcher: Execution web search for: {state['query']}")
    # Simulate search
    result = f"Found relevant information for {state['query']} from multiple sources."
    return {"research_results": state.get("research_results", []) + [result]}

def analyst_node(state: ResearchState):
    logger.info("Analyst: Processing gathered research data.")
    # Simulate analysis
    analysis = f"Synthesis of data: {state['research_results'][-1]}"
    return {"analysis": analysis}

def create_research_graph():
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add edges
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next_step"],
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "END": END
        }
    )
    
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    return workflow.compile()

if __name__ == "__main__":
    logger.info("Initializing deer-flow inspired research graph...")
    graph = create_research_graph()
    logger.success("Research graph compiled successfully.")
