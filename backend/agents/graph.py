from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from .state import AgentState
from .memory import get_thread_history, retrieve_persistent_memory
from ..deps import lc_llm
import logging

logger = logging.getLogger(__name__)

def build_prompt(system_prompt: str) -> ChatPromptTemplate:
    """Build chat prompt template with system, history, and human components"""
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("history"),
        ("human", "{input}")
    ])

def make_chain(system_prompt: str):
    """Create chain with message history"""
    prompt = build_prompt(system_prompt)
    llm = lc_llm()
    base_chain = prompt | llm
    
    return RunnableWithMessageHistory(
        base_chain,
        lambda config: get_thread_history(config["configurable"]["session_id"]),
        input_messages_key="input",
        history_messages_key="history",
    )

# Graph nodes
def n_prepare(state: AgentState) -> AgentState:
    """Prepare node - retrieve persistent memory if enabled"""
    if state.get("persist_memory", False):
        # Retrieve relevant docs from pgvector
        docs = retrieve_persistent_memory(
            state["tenant_id"], 
            state["agent_id"], 
            state["input"]
        )
        state["docs"] = docs
        logger.info(f"Retrieved {len(docs)} docs from persistent memory")
    else:
        state["docs"] = []
    
    return state

def n_llm(state: AgentState) -> AgentState:
    """LLM node - generate response using chain with history"""
    try:
        # Add retrieved docs to system prompt if available
        system_prompt = state["system_prompt"]
        if state.get("docs"):
            docs_context = "\n\nRelevant context:\n" + "\n".join(state["docs"])
            system_prompt += docs_context
        
        chain = make_chain(system_prompt)
        session_key = f"{state['tenant_id']}:{state['agent_id']}:{state['session_id']}"
        
        result = chain.invoke(
            {"input": state["input"]},
            config={"configurable": {"session_id": session_key}}
        )
        
        state["response"] = result.content.strip()
        logger.info(f"Generated response for session {session_key}")
        
    except Exception as e:
        logger.error(f"LLM generation failed: {str(e)}")
        state["response"] = "I apologize, but I'm having trouble responding right now. Please try again or contact support."
    
    return state

def n_summarize(state: AgentState) -> AgentState:
    """Summarize node - create CRM notes"""
    response = state.get("response", "")
    user_input = state.get("input", "")
    
    # Simple summary for CRM (keep under 600 chars)
    summary = f"User: {user_input[:200]}... Agent responded with assistance."
    if len(summary) > 600:
        summary = summary[:597] + "..."
    
    state["notes_for_crm"] = summary
    
    return state

def compile_graph():
    """Compile the LangGraph workflow"""
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("prepare", n_prepare)
    graph.add_node("llm", n_llm)
    graph.add_node("summarize", n_summarize)
    
    # Define edges
    graph.set_entry_point("prepare")
    graph.add_edge("prepare", "llm")
    graph.add_edge("llm", "summarize")
    graph.add_edge("summarize", END)
    
    return graph.compile()