from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
import os

def create_index():
    schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True), url=ID(stored=True))
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
    writer = ix.writer()

    writer.add_document(
        title="Blockchain",
        content="A blockchain is a decentralized ledger of transactions, maintained across multiple computers, ensuring security and transparency.",
        url="https://en.wikipedia.org/wiki/Blockchain"
    )
    writer.add_document(
        title="Artificial Intelligence",
        content="Artificial intelligence (AI) is the simulation of human intelligence in machines, enabling tasks like reasoning and learning.",
        url="https://en.wikipedia.org/wiki/Artificial_intelligence"
    )
    writer.commit()

if __name__ == "__main__":
    create_index()