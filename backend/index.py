# backend/index.py (Enhanced Version)
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, DATETIME
import os
from datetime import datetime

def create_index():
    # Enhanced schema with more fields
    schema = Schema(
        title=TEXT(stored=True),
        content=TEXT(stored=True),
        url=ID(stored=True),
        created=DATETIME(stored=True)
    )

    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    ix = create_in("indexdir", schema)
    writer = ix.writer()

    # Add more comprehensive sample documents
    documents = [
        {
            "title": "Blockchain Technology",
            "content": "A blockchain is a decentralized, distributed ledger technology that maintains a continuously growing list of records, called blocks, which are linked and secured using cryptography. Each block contains a cryptographic hash of the previous block, a timestamp, and transaction data. Blockchain technology enables secure, transparent, and tamper-resistant record-keeping without the need for a central authority. It's the underlying technology behind cryptocurrencies like Bitcoin and Ethereum, but has applications in supply chain management, digital identity, smart contracts, and many other fields.",
            "url": "https://en.wikipedia.org/wiki/Blockchain"
        },
        {
            "title": "Artificial Intelligence",
            "content": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning (the acquisition of information and rules for using the information), reasoning (using rules to reach approximate or definite conclusions), and self-correction. AI applications include expert systems, natural language processing, speech recognition, and machine vision. Modern AI techniques include machine learning, deep learning, neural networks, and natural language processing. AI is used in various fields such as healthcare, finance, transportation, and entertainment.",
            "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
        },
        {
            "title": "Machine Learning",
            "content": "Machine Learning is a subset of artificial intelligence that focuses on the development of algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience. Machine learning algorithms build mathematical models based on training data to make predictions or decisions without being explicitly programmed to perform the task. Types include supervised learning, unsupervised learning, and reinforcement learning. Applications include image recognition, recommendation systems, fraud detection, and predictive analytics.",
            "url": "https://en.wikipedia.org/wiki/Machine_learning"
        },
        {
            "title": "Cloud Computing",
            "content": "Cloud computing is the on-demand availability of computer system resources, especially data storage and computing power, without direct active management by the user. The term is generally used to describe data centers available to many users over the Internet. Large clouds, predominant today, often have functions distributed over multiple locations from central servers. Cloud computing relies on sharing of resources to achieve coherence and economies of scale. Types include Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS).",
            "url": "https://en.wikipedia.org/wiki/Cloud_computing"
        },
        {
            "title": "Cybersecurity",
            "content": "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information; extorting money from users; or interrupting normal business processes. Implementing effective cybersecurity measures is particularly challenging today because there are more devices than people, and attackers are becoming more innovative. Key areas include network security, application security, information security, operational security, disaster recovery, and end-user education.",
            "url": "https://en.wikipedia.org/wiki/Computer_security"
        },
        {
            "title": "Internet of Things (IoT)",
            "content": "The Internet of Things describes the network of physical objects—'things'—that are embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices and systems over the Internet. These devices range from ordinary household objects to sophisticated industrial tools. IoT enables objects to be sensed or controlled remotely across existing network infrastructure, creating opportunities for more direct integration of the physical world into computer-based systems. Applications include smart homes, wearable devices, connected cars, and industrial IoT.",
            "url": "https://en.wikipedia.org/wiki/Internet_of_things"
        },
        {
            "title": "Data Science",
            "content": "Data science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. Data science is related to data mining, machine learning, and big data. It combines domain expertise, programming skills, and knowledge of mathematics and statistics to extract meaningful insights from data. The data science process typically includes data collection, cleaning, exploration, analysis, visualization, and interpretation. Tools commonly used include Python, R, SQL, Tableau, and various machine learning frameworks.",
            "url": "https://en.wikipedia.org/wiki/Data_science"
        },
        {
            "title": "Quantum Computing",
            "content": "Quantum computing is a type of computation that harnesses the collective properties of quantum states, such as superposition, interference, and entanglement, to perform calculations. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits (qubits) that can exist in multiple states simultaneously. This allows quantum computers to potentially solve certain problems exponentially faster than classical computers. Applications include cryptography, optimization problems, drug discovery, and financial modeling. Current challenges include maintaining quantum coherence and error correction.",
            "url": "https://en.wikipedia.org/wiki/Quantum_computing"
        }
    ]

    # Add all documents to the index
    current_time = datetime.now()
    for doc in documents:
        writer.add_document(
            title=doc["title"],
            content=doc["content"],
            url=doc["url"],
            created=current_time
        )

    writer.commit()
    print(f"Index created successfully with {len(documents)} documents")

if __name__ == "__main__":
    create_index()