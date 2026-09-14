from langgraph.graph import StateGraph, START, END

from state import NewsLetterState

from nodes.planner import planner_node
from nodes.news_agent import news_agent_node
from nodes.image_agent import image_agent_node
from nodes.writer import writer_node
from nodes.exporter import exporter_node

from nodes.gmail_agent import gmail_email_node


# =========================================================
# CREATE GRAPH
# =========================================================

graph = StateGraph(NewsLetterState)


# =========================================================
# ADD NODES
# =========================================================

graph.add_node(
    "planner",
    planner_node
)

graph.add_node(
    "news_agent",
    news_agent_node
)

graph.add_node(
    "image_agent",
    image_agent_node
)

graph.add_node(
    "writer",
    writer_node
)

graph.add_node(
    "exporter",
    exporter_node
)

graph.add_node(
    "email",
    gmail_email_node
)


# =========================================================
# FLOW
# =========================================================

graph.add_edge(
    START,
    "planner"
)

graph.add_edge(
    "planner",
    "news_agent"
)

graph.add_edge(
    "news_agent",
    "image_agent"
)

graph.add_edge(
    "image_agent",
    "writer"
)

graph.add_edge(
    "writer",
    "exporter"
)

graph.add_edge(
    "exporter",
    "email"
)

graph.add_edge(
    "email",
    END
)


# =========================================================
# COMPILE
# =========================================================

app = graph.compile()