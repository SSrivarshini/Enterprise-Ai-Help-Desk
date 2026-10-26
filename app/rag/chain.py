"""RAG answering with a fallback + escalation workflow for unanswered queries."""
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import CONTACTS_FILE, LLM_MODEL, RELEVANCE_THRESHOLD, TOP_K
from app.rag.vectorstore import get_vectorstore

NO_ANSWER = "NO_ANSWER"

PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an internal help desk assistant for employees. "
            "Answer ONLY from the context below. If the context does not contain the answer, "
            f"reply with exactly {NO_ANSWER}. Be concise and clear, use short steps where helpful, "
            "and never invent policies, numbers or dates.",
        ),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)

CATEGORY_KEYWORDS = {
    "payroll": ["salary", "payslip", "payroll", "reimbursement", "tax", "bonus", "expense"],
    "it": ["password", "laptop", "vpn", "software", "email access", "2fa", "wifi", "network", "device"],
    "hr": ["leave", "onboarding", "joining", "policy", "probation", "resign", "notice", "appraisal", "benefit"],
}


def detect_category(question: str) -> str:
    q = question.lower()
    for category, words in CATEGORY_KEYWORDS.items():
        if any(w in q for w in words):
            return category
    return "general"


def fallback_message(question: str) -> str:
    contacts = json.loads(CONTACTS_FILE.read_text(encoding="utf-8"))
    contact = contacts.get(detect_category(question), contacts["general"])
    return (
        "I couldn't find this in the company knowledge base. "
        f"Please contact {contact['team']} at {contact['email']} ({contact['hours']}) "
        "and they will help you."
    )


class HelpDesk:
    def __init__(self):
        self.store = get_vectorstore()
        self.llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

    def ask(self, question: str) -> dict:
        results = self.store.similarity_search_with_relevance_scores(question, k=TOP_K)
        relevant = [(doc, score) for doc, score in results if score >= RELEVANCE_THRESHOLD]

        if not relevant:
            return {"answer": fallback_message(question), "fallback": True, "sources": []}

        context = "\n\n".join(doc.page_content for doc, _ in relevant)
        answer = (PROMPT | self.llm).invoke({"context": context, "question": question}).content.strip()

        if NO_ANSWER in answer:
            return {"answer": fallback_message(question), "fallback": True, "sources": []}

        sources = sorted({doc.metadata.get("source", "unknown") for doc, _ in relevant})
        return {"answer": answer, "fallback": False, "sources": sources}
