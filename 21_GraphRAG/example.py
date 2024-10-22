import json
import os
from typing import List, Dict, Any
import networkx as nx
from cdlib import algorithms
from openai import OpenAI
import textwrap


class GraphRAGPipeline:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the pipeline with API credentials and configurations
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def split_documents_into_chunks(self, documents: List[str], chunk_size: int = 600, overlap_size: int = 100) -> List[
        str]:
        """Split documents into overlapping chunks"""
        chunks = []
        for document in documents:
            for i in range(0, len(document), chunk_size - overlap_size):
                chunk = document[i:i + chunk_size]
                chunks.append(chunk)
        return chunks

    def extract_elements_from_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Extract entities and relationships from text chunks"""
        elements = []
        for index, chunk in enumerate(chunks):
            print(f"Processing chunk {index + 1}/{len(chunks)}")
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": """Extract entities and relationships from the text. Return JSON only.
                    {
                        "entities": ["entity1", "entity2"],
                        "relationships": [
                            {
                                "source": "entity1",
                                "target": "entity2",
                                "relationship": "relationship description"
                            }
                        ]
                    }"""},
                    {"role": "user", "content": chunk}
                ]
            )
            try:
                parsed_response = json.loads(response.choices[0].message.content)
                elements.append(parsed_response)
            except json.JSONDecodeError as e:
                print(f"Warning: JSON parse error in chunk {index}: {e}")
                elements.append({"entities": [], "relationships": []})
        return elements

    def build_graph_from_summaries(self, summaries: List[Dict[str, Any]]) -> nx.Graph:
        """Build a NetworkX graph from the summarized elements"""
        G = nx.Graph()
        for summary in summaries:
            for entity in summary.get("entities", []):
                G.add_node(entity)
            for rel in summary.get("relationships", []):
                source = rel.get("source")
                target = rel.get("target")
                relationship = rel.get("relationship")
                if source and target:
                    G.add_edge(source, target, label=relationship)
        return G

    def detect_communities(self, graph: nx.Graph) -> List[List[str]]:
        """Detect communities in the graph"""
        communities = []
        for component in nx.connected_components(graph):
            subgraph = graph.subgraph(component)
            if len(subgraph.nodes) > 1:
                try:
                    sub_communities = algorithms.leiden(subgraph)
                    for community in sub_communities.communities:
                        communities.append(list(community))
                except Exception as e:
                    print(f"Warning: Community detection error: {e}")
                    communities.append(list(subgraph.nodes))
            else:
                communities.append(list(subgraph.nodes))
        return communities

    def summarize_communities(self, communities: List[List[str]], graph: nx.Graph) -> List[Dict[str, Any]]:
        """Generate summaries for each community"""
        community_summaries = []
        for index, community in enumerate(communities):
            print(f"Summarizing community {index + 1}/{len(communities)}")
            subgraph = graph.subgraph(community)
            community_data = {
                "entities": list(subgraph.nodes),
                "relationships": [
                    {
                        "source": edge[0],
                        "target": edge[1],
                        "relationship": edge[2]["label"]
                    }
                    for edge in subgraph.edges(data=True)
                ]
            }

            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": """Summarize the community. Return JSON only.
                    {
                        "summary": "Brief summary text",
                        "main_themes": ["theme1", "theme2"],
                        "key_entities": ["entity1", "entity2"]
                    }"""},
                    {"role": "user", "content": json.dumps(community_data)}
                ]
            )
            try:
                parsed_summary = json.loads(response.choices[0].message.content)
                community_summaries.append(parsed_summary)
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse JSON for community {index}")
                community_summaries.append({
                    "summary": "",
                    "main_themes": [],
                    "key_entities": []
                })
        return community_summaries

    def generate_final_answer(self, community_summaries: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate final answer based on community summaries"""
        intermediate_answers = []

        for index, summary in enumerate(community_summaries):
            print(f"Generating answer for community {index + 1}/{len(community_summaries)}")
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": """Answer the query based on the summary. Return JSON only.
                    {
                        "answer": "detailed answer",
                        "confidence": 0.0-1.0,
                        "supporting_evidence": ["evidence1", "evidence2"]
                    }"""},
                    {"role": "user", "content": f"Query: {query}\nSummary: {json.dumps(summary)}"}
                ]
            )
            try:
                parsed_answer = json.loads(response.choices[0].message.content)
                intermediate_answers.append(parsed_answer)
            except json.JSONDecodeError:
                print(f"Warning: Failed to parse JSON for summary {index}")
                intermediate_answers.append({
                    "answer": "",
                    "confidence": 0.0,
                    "supporting_evidence": []
                })

        final_response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """Combine the answers into a final response. Return JSON only.
                {
                    "final_answer": "comprehensive answer",
                    "confidence": 0.0-1.0,
                    "main_points": ["point1", "point2"],
                    "sources": ["source1", "source2"]
                }"""},
                {"role": "user", "content": json.dumps(intermediate_answers)}
            ]
        )

        try:
            return json.loads(final_response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "final_answer": "",
                "confidence": 0.0,
                "main_points": [],
                "sources": []
            }

    def process(self, documents: List[str], query: str, chunk_size: int = 600, overlap_size: int = 100) -> Dict[
        str, Any]:
        """Main processing pipeline"""
        print("1. Splitting documents into chunks...")
        chunks = self.split_documents_into_chunks(documents, chunk_size, overlap_size)

        print("2. Extracting elements from chunks...")
        elements = self.extract_elements_from_chunks(chunks)

        print("3. Building knowledge graph...")
        graph = self.build_graph_from_summaries(elements)

        print("4. Detecting communities...")
        communities = self.detect_communities(graph)

        print("5. Summarizing communities...")
        community_summaries = self.summarize_communities(communities, graph)

        print("6. Generating final answer...")
        final_answer = self.generate_final_answer(community_summaries, query)

        return final_answer


def main():
    # Load API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set OPENAI_API_KEY environment variable")

    # Initialize pipeline
    pipeline = GraphRAGPipeline(api_key=api_key)

    # Get user input
    print("\nWelcome to the Document Analysis System")
    print("=======================================")

    # Get documents from user
    documents = []
    print("\nPlease enter your documents (enter an empty line to finish):")
    while True:
        line = input()
        if not line:
            break
        documents.append(line)

    if not documents:
        print("No documents provided. Exiting...")
        return

    # Get query from user
    print("\nPlease enter your question about the documents:")
    query = input()

    if not query:
        print("No query provided. Exiting...")
        return

    # Process the documents
    try:
        print("\nProcessing your request...")
        result = pipeline.process(documents, query)

        # Display results
        print("\nResults:")
        print("========")
        print(f"\nFinal Answer: {result['final_answer']}")
        print(f"\nConfidence: {result['confidence']:.2f}")

        if result['main_points']:
            print("\nMain Points:")
            for point in result['main_points']:
                print(f"- {point}")

        if result['sources']:
            print("\nSources:")
            for source in result['sources']:
                print(f"- {source}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")


if __name__ == "__main__":
    main()